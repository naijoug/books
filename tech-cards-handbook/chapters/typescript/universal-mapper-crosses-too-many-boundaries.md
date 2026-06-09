# 不要用万能 mapper 跨多条边界

**问题**：

边界越多，越容易出现一个看似省事的 `mapProduct`、`convertOrder` 或 `normalizeUser`：它既解析外部输入，又脱敏 DTO，又格式化页面文案，还顺手构造 command 或 event。短期少写了几个函数，长期却让任何字段变动都牵动多个层次；一次页面展示调整可能破坏 API 契约，一次 DTO 版本演进也可能污染领域模型。

**要点**：

- 一个 mapper 只跨越一条边界，例如 `toProductResponseDto` 只负责领域模型到响应 DTO。
- 函数名要说清楚方向和目标：`parseXxx`、`toXxxDto`、`toXxxViewModel`、`toXxxCommand`、`toXxxEvent`。
- 不同边界的变化原因不同：API DTO 跟权限和版本有关，ViewModel 跟页面展示有关，Command 跟业务动作有关，Event 跟事实记录和订阅者有关。
- 共享通用小函数可以，例如 `formatMoney`、`parseMoneyInput`；不要共享一个包含业务决策和多层字段拼装的“大 mapper”。
- 如果 mapper 需要同时接收 `request`、`domain model`、`ui state` 和 `eventId`，通常说明它跨了太多边界，应该拆开。

**示例**：

```typescript
type Brand<T, Name extends string> = T & { readonly __brand: Name };

type ProductId = Brand<string, "ProductId">;
type SellerId = Brand<string, "SellerId">;

type Product = {
  id: ProductId;
  sellerId: SellerId;
  name: string;
  priceCents: number;
  currency: "CNY" | "USD";
  status: "draft" | "published" | "archived";
  publishedAt: Date | null;
  internalCostCents: number;
};

type ProductResponseDto = {
  id: string;
  name: string;
  price: {
    cents: number;
    currency: "CNY" | "USD";
  };
  status: "draft" | "published" | "archived";
  detailsUrl: string;
};

type ProductListItemViewModel = {
  id: string;
  title: string;
  priceText: string;
  badge: "草稿" | "已发布" | "已归档";
  href: string;
  selected: boolean;
};

type ProductFormViewModel = {
  productId: string;
  nameInput: string;
  priceInput: string;
  isDirty: boolean;
  submitLabel: string;
  errors: Record<string, string>;
};

type UpdateProductCommand = {
  productId: ProductId;
  name: string;
  priceCents: number;
};

type ProductPublishedEvent = {
  type: "ProductPublished";
  productId: string;
  sellerId: string;
  occurredAt: string;
};

type CommandResult =
  | { ok: true; value: UpdateProductCommand }
  | { ok: false; error: string };

function formatMoney(cents: number, currency: "CNY" | "USD"): string {
  return `${currency} ${(cents / 100).toFixed(2)}`;
}

function parseMoneyInput(input: string): number | null {
  const value = Number(input.trim());
  if (!Number.isFinite(value) || value < 0) {
    return null;
  }
  return Math.round(value * 100);
}

function toProductResponseDto(product: Product): ProductResponseDto {
  return {
    id: product.id,
    name: product.name,
    price: {
      cents: product.priceCents,
      currency: product.currency,
    },
    status: product.status,
    detailsUrl: `/products/${product.id}`,
  };
}

function toProductListItemViewModel(
  dto: ProductResponseDto,
  selectedProductIds: ReadonlySet<string>,
): ProductListItemViewModel {
  const badgeByStatus: Record<ProductResponseDto["status"], ProductListItemViewModel["badge"]> = {
    draft: "草稿",
    published: "已发布",
    archived: "已归档",
  };

  return {
    id: dto.id,
    title: dto.name,
    priceText: formatMoney(dto.price.cents, dto.price.currency),
    badge: badgeByStatus[dto.status],
    href: dto.detailsUrl,
    selected: selectedProductIds.has(dto.id),
  };
}

function toUpdateProductCommand(form: ProductFormViewModel): CommandResult {
  const name = form.nameInput.trim();
  const priceCents = parseMoneyInput(form.priceInput);

  if (name.length === 0 || priceCents === null) {
    return { ok: false, error: "name and price are required" };
  }

  return {
    ok: true,
    value: {
      productId: form.productId as ProductId,
      name,
      priceCents,
    },
  };
}

function toProductPublishedEvent(product: Product, occurredAt: Date): ProductPublishedEvent {
  if (product.status !== "published") {
    throw new Error("ProductPublished event requires published product");
  }

  return {
    type: "ProductPublished",
    productId: product.id,
    sellerId: product.sellerId,
    occurredAt: occurredAt.toISOString(),
  };
}

const product: Product = {
  id: "product_1" as ProductId,
  sellerId: "seller_1" as SellerId,
  name: "TypeScript Card",
  priceCents: 9900,
  currency: "CNY",
  status: "published",
  publishedAt: new Date("2026-06-09T02:30:00.000Z"),
  internalCostCents: 1800,
};

const dto = toProductResponseDto(product);
const item = toProductListItemViewModel(dto, new Set(["product_1"]));
const command = toUpdateProductCommand({
  productId: dto.id,
  nameInput: "TypeScript Boundary Card",
  priceInput: "109.00",
  isDirty: true,
  submitLabel: "保存",
  errors: {},
});
const publishedEvent = toProductPublishedEvent(product, new Date("2026-06-09T02:31:00.000Z"));

console.log(item.priceText, command.ok, publishedEvent.type);
```

把代码块保存为 `universal-mapper-crosses-too-many-boundaries.ts` 后，可用下面的命令做最小编译验证：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom universal-mapper-crosses-too-many-boundaries.ts
```

这里共享的是无状态小函数 `formatMoney` 和 `parseMoneyInput`；真正跨边界的函数仍然拆成四个：领域模型到 DTO、DTO 到 ViewModel、表单 ViewModel 到 Command、领域模型到 Event。这样页面是否选中、API 是否脱敏、提交字段如何校验、事件何时发布，都不会挤进同一个 `mapProduct`。

**坑**：

- 不要写 `mapProduct(product, options)`，再用 `options.mode = "dto" | "view" | "event"` 控制不同输出；这种分支会把多个边界重新揉回一个函数。
- 不要让 DTO mapper 读取页面选中态、按钮文案或表单错误；这些属于 ViewModel。
- 不要让 ViewModel mapper 顺手构造业务 command；提交动作应有独立的 `toXxxCommand`。
- 不要在 event mapper 里补做支付、发布、审核等业务决策；事件 mapper 只记录已发生事实。
- 不要为了复用而返回 `any` 或超大联合类型；类型系统会失去提醒边界泄漏的能力。

**检查**：

- mapper 函数名是否能明确说出 `from` 和 `to`；说不清时是否已经拆开。
- 每个 mapper 是否只接收当前边界需要的数据，而不是拿到整条请求上下文。
- API 字段、UI 文案、业务 command、event payload 是否能分别演进。
- 共享函数是否足够小、纯粹、无边界语义；一旦它开始知道 DTO / ViewModel / Event，就应该下沉回对应 mapper。
