# URL 状态应该留在 URL

**问题**：

筛选条件、搜索词、分页、排序和 tab 经常既影响列表数据，又需要支持刷新、分享链接和浏览器前进后退。如果把这些值只放进组件 `useState`，URL 变成摆设：用户刷新会丢状态，复制链接不能复现当前视图，后退按钮也可能只改地址不改界面。

**要点**：

- 会影响“当前页面位置”的状态，优先放在 URL query、path segment 或 hash 中。
- 组件可以从 URL 解析出渲染所需值，但不要再维护一份长期同步的本地副本。
- 输入框正在编辑、下拉菜单临时展开、modal 内草稿等短暂 UI 状态，仍适合留在局部 state。
- 写 URL 时要集中规范化：默认值不写入、非法值回退、数字和枚举先校验再使用。
- 请求缓存 key 应该直接包含规范化后的 URL 状态，而不是读取另一个可能过期的本地 state。

**示例**：

```tsx
import { useMemo } from "react";

type SortKey = "newest" | "price_asc" | "price_desc";

type ProductQuery = {
  keyword: string;
  page: number;
  sort: SortKey;
};

const SORT_KEYS: SortKey[] = ["newest", "price_asc", "price_desc"];

function parseProductQuery(search: string): ProductQuery {
  const params = new URLSearchParams(search);
  const sort = params.get("sort");
  const rawPage = Number(params.get("page") ?? "1");

  return {
    keyword: params.get("q")?.trim() ?? "",
    page: Number.isInteger(rawPage) && rawPage > 0 ? rawPage : 1,
    sort: sort !== null && SORT_KEYS.includes(sort as SortKey) ? (sort as SortKey) : "newest",
  };
}

function buildProductSearch(next: ProductQuery): string {
  const params = new URLSearchParams();
  if (next.keyword !== "") params.set("q", next.keyword);
  if (next.page !== 1) params.set("page", String(next.page));
  if (next.sort !== "newest") params.set("sort", next.sort);
  return params.toString();
}

export function ProductListPage({ locationSearch }: { locationSearch: string }) {
  const query = useMemo(() => parseProductQuery(locationSearch), [locationSearch]);
  const cacheKey = ["products", query.keyword, query.page, query.sort].join(":");

  function replaceQuery(next: ProductQuery) {
    const nextSearch = buildProductSearch(next);
    window.history.replaceState(null, "", nextSearch === "" ? "/products" : `/products?${nextSearch}`);
  }

  return (
    <section data-cache-key={cacheKey}>
      <input
        value={query.keyword}
        onChange={(event: { currentTarget: { value: string } }) =>
          replaceQuery({ ...query, keyword: event.currentTarget.value, page: 1 })
        }
      />
      <button onClick={() => replaceQuery({ ...query, sort: "price_asc", page: 1 })}>
        Sort by price
      </button>
      <p>Page {query.page}</p>
    </section>
  );
}
```

这里 `keyword`、`page` 和 `sort` 都来自 URL。刷新页面、复制链接或浏览器前进后退时，组件只需要重新解析 `locationSearch`，不需要 Effect 去追赶同步另一份本地筛选 state。

**坑**：

- URL 和 `useState` 各维护一份筛选条件，再用 Effect 互相同步：很容易出现循环更新、旧请求 key 和历史记录污染。
- 把输入框每一个按键都 `pushState` 成一条历史记录，导致后退按钮要退很多次；高频编辑通常用 `replaceState` 或提交后再 `pushState`。
- 不校验 URL 参数，直接把 `page=-1`、`sort=unknown` 或超长搜索词传给请求层。
- 把所有 UI 状态都塞进 URL：hover、菜单展开、未提交草稿等只服务当前交互的状态不需要可分享。

**检查**：

- 刷新页面后，列表筛选、排序、分页是否仍能复现？
- 复制当前链接给别人，是否能看到同一个业务视图，而不是默认列表？
- 浏览器前进/后退时，UI、请求缓存 key 和地址栏是否一致变化？
- URL 参数是否有统一解析、默认值和非法值回退，而不是散落在多个组件里？
- 哪些状态只是瞬时 UI 反馈？它们是否没有被过度持久化到 URL？
