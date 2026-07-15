# `unknown` 在抽象方法签名中作为传输类型

**问题**：当模板方法模式的基类需要声明 `fetch`/`parse`/`transform` 等抽象方法时，返回值应该用什么类型？子类各自处理不同的数据源（API JSON、HTML、RSS），统一声明成 `any` 会关闭类型检查，声明成泛型又会把所有子类绑定到同一个数据形状。

**要点**：

- 把抽象方法的返回值声明为 `unknown`，子类再各自缩窄到具体类型（API 响应对象、HTML 字符串、Cheerio 元素等）。
- 模板方法只依赖 `unknown` 级别的契约：`fetch(): Promise<unknown>` 交给 `parse(data: unknown): Promise<unknown[]>`，再交给 `transform(items: unknown[])`。
- 每个子类在自己的实现里完成缩窄：`ApiCrawler.parse` 检查 `dataPath` 返回的是否为数组，`StaticCrawler.parse` 检查 `typeof html === 'string'` 后加载 Cheerio。
- 比 `any` 更安全：编译器拒绝直接访问属性；比泛型更松散：不同子类不需要共享同一个 `T`。
- 如果子类的中间类型有复用价值（如 `StaticParsedItem`），可以把它定义在子类文件里，而不是强制基类感知。

**示例**：

```typescript
type NewsItem = {
  title: string;
  url: string;
  publishTime: Date;
  platformId: string;
  crawlTime: Date;
};

// BaseCrawler: template method depends on unknown-level contract
abstract class BaseCrawler {
  async crawl(): Promise<NewsItem[]> {
    const rawData = await this.fetch();
    const parsed = await this.parse(rawData);
    return this.transform(parsed);
  }

  protected abstract fetch(): Promise<unknown>;
  protected abstract parse(data: unknown): Promise<unknown[]>;
  protected abstract transformItem(
    item: unknown,
  ): Omit<NewsItem, "platformId" | "crawlTime">;

  // transform can iterate unknown[] and delegate per-item narrowing to subclass
  protected transform(items: unknown[]): NewsItem[] {
    return items
      .map((item) => {
        try {
          return this.transformItem(item);
        } catch {
          return null;
        }
      })
      .filter((item): item is NewsItem => item !== null);
  }
}

// Stub types representing external library shapes
type ApiResponse = { data: unknown };
type AnyNode = { type: string; children: unknown[] };
type CheerioAPI = { (selector: string): void };
type StaticParsedItem = { element: AnyNode; $: CheerioAPI };

// ApiCrawler narrows unknown to API response → extract via dataPath
class ApiCrawler extends BaseCrawler {
  protected async fetch(): Promise<unknown> {
    const response: ApiResponse = { data: [{ title: "hello" }] };
    return response.data;
  }

  protected async parse(data: unknown): Promise<unknown[]> {
    return Array.isArray(data) ? data : [];
  }

  protected transformItem(
    item: unknown,
  ): Omit<NewsItem, "platformId" | "crawlTime"> {
    if (typeof item !== "object" || item === null || !("title" in item)) {
      throw new Error("missing title");
    }
    const title = (item as Record<string, unknown>).title;
    if (typeof title !== "string") throw new Error("title must be string");
    return { title, url: "https://example.com", publishTime: new Date() };
  }
}

// StaticCrawler narrows unknown to HTML string → parsed elements
class StaticCrawler extends BaseCrawler {
  protected async fetch(): Promise<string> {
    // override return type: string is assignable to unknown
    return "<html></html>";
  }

  protected async parse(html: unknown): Promise<StaticParsedItem[]> {
    if (typeof html !== "string") throw new Error("expected HTML string");
    return [];
  }

  protected transformItem(
    item: unknown,
  ): Omit<NewsItem, "platformId" | "crawlTime"> {
    if (!isStaticParsedItem(item)) throw new Error("invalid item");
    return {
      title: "example",
      url: "https://example.com",
      publishTime: new Date(),
    };
  }
}

function isStaticParsedItem(item: unknown): item is StaticParsedItem {
  return (
    typeof item === "object" &&
    item !== null &&
    "element" in item &&
    "$" in item &&
    typeof (item as Record<string, unknown>).$ === "function"
  );
}
```

最小验证：把上面的代码保存为 `unknown-transit-type-in-abstract-hierarchies.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom unknown-transit-type-in-abstract-hierarchies.ts`；如果没有类型错误，说明模板方法只依赖 `unknown` 契约就能编排不同子类的具体数据源。

**坑**：

- 不要在基类模板方法里直接访问 `unknown` 值的属性（如 `rawData.items`）；编译器会报错，这正是 `unknown` 的保护效果。
- 不要为了"方便"把抽象方法返回值改回 `any` 以绕过编译错误；正确做法是在子类内部完成缩窄，或在基类里补充 `isRecord` 等通用守卫。
- TypeScript 允许子类 override 时缩窄返回类型（`Promise<string>` 替代 `Promise<unknown>`），但不允许放宽（`Promise<any>` 不应该作为 override 出现）。

**检查**：当一个抽象类有多个子类处理不同的外部数据源时，把抽象方法的返回值和参数声明为 `unknown`；每个子类在自己的实现里用 `typeof`、`Array.isArray`、自定义守卫或第三方库类型完成缩窄。模板方法只调用抽象方法、不直接访问数据内部结构。
