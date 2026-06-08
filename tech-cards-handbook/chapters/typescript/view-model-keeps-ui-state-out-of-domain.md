# ViewModel 不要污染领域模型

**问题**：

页面经常需要展示标签、按钮状态、选中态、格式化价格、相对时间和跳转链接。如果为了方便把这些 UI 字段直接加到领域模型上，模型会越来越像页面临时状态；后端契约、业务逻辑和测试也会被展示需求牵着走。

**要点**：

- 领域模型表达业务事实，ViewModel 表达当前界面的展示需要；不要为了一个页面把 `isSelected`、`label`、`href`、`badgeText` 塞进领域类型。
- ViewModel 应由领域模型、用户上下文和页面状态纯函数派生，方便测试和复用。
- 领域模型中的 `Date`、品牌 ID、枚举、金额等可以在 ViewModel 边界格式化成字符串或展示分组。
- 列表页、详情页、表单页可以有不同 ViewModel；不要强求一个“万能前端模型”。
- ViewModel 不能反向写回业务层；提交时应构造明确的 `Command` / `Dto`。

**示例**：

```typescript
type Brand<T, Name extends string> = T & { readonly __brand: Name };

type ProductId = Brand<string, "ProductId">;

type Product = {
  id: ProductId;
  name: string;
  priceCents: number;
  status: "draft" | "published" | "archived";
  inventory: number;
  updatedAt: Date;
};

type ProductListState = {
  selectedIds: ReadonlySet<ProductId>;
  now: Date;
  locale: "zh-CN" | "en-US";
};

type ProductListItemViewModel = {
  id: string;
  title: string;
  priceText: string;
  statusLabel: string;
  inventoryBadge: "有库存" | "库存紧张" | "已售罄";
  isSelected: boolean;
  canEdit: boolean;
  href: string;
  updatedText: string;
};

function formatPrice(cents: number, locale: ProductListState["locale"]): string {
  const currency = locale === "zh-CN" ? "CNY" : "USD";
  const amount = currency === "CNY" ? cents / 100 : cents / 100 / 7;

  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(amount);
}

function toStatusLabel(status: Product["status"]): string {
  switch (status) {
    case "draft":
      return "草稿";
    case "published":
      return "已发布";
    case "archived":
      return "已归档";
  }
}

function toInventoryBadge(inventory: number): ProductListItemViewModel["inventoryBadge"] {
  if (inventory <= 0) return "已售罄";
  if (inventory < 5) return "库存紧张";
  return "有库存";
}

function formatRelativeDays(updatedAt: Date, now: Date): string {
  const millisecondsPerDay = 24 * 60 * 60 * 1000;
  const days = Math.max(0, Math.floor((now.getTime() - updatedAt.getTime()) / millisecondsPerDay));

  if (days === 0) return "今天更新";
  return `${days} 天前更新`;
}

function toProductListItemViewModel(
  product: Product,
  state: ProductListState,
): ProductListItemViewModel {
  const inventoryBadge = toInventoryBadge(product.inventory);

  return {
    id: product.id,
    title: product.name,
    priceText: formatPrice(product.priceCents, state.locale),
    statusLabel: toStatusLabel(product.status),
    inventoryBadge,
    isSelected: state.selectedIds.has(product.id),
    canEdit: product.status !== "archived",
    href: `/products/${product.id}`,
    updatedText: formatRelativeDays(product.updatedAt, state.now),
  };
}

type UpdateProductNameCommand = {
  productId: ProductId;
  name: string;
};

function toUpdateProductNameCommand(
  product: Product,
  nextName: string,
): UpdateProductNameCommand {
  return {
    productId: product.id,
    name: nextName.trim(),
  };
}

const product: Product = {
  id: "product_1" as ProductId,
  name: "AI Prompt 手册",
  priceCents: 9900,
  status: "published",
  inventory: 3,
  updatedAt: new Date("2026-06-01T00:00:00.000Z"),
};

const viewModel = toProductListItemViewModel(product, {
  selectedIds: new Set<ProductId>([product.id]),
  now: new Date("2026-06-09T00:00:00.000Z"),
  locale: "zh-CN",
});

const command = toUpdateProductNameCommand(product, " AI Prompt 模板手册 ");

console.log(viewModel.title, viewModel.inventoryBadge, viewModel.href, command.name);
```

把代码块保存为 `view-model-keeps-ui-state-out-of-domain.ts` 后，可用下面的命令做最小编译验证：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom view-model-keeps-ui-state-out-of-domain.ts
```

示例里 `Product` 没有 `isSelected`、`priceText`、`href`、`updatedText`。这些字段只属于当前列表页 ViewModel；真正提交给业务层的是 `UpdateProductNameCommand`，而不是把 ViewModel 原样传回去。

**坑**：

- 不要在领域模型上追加 `label`、`checked`、`disabled`、`href` 这类页面字段；多个页面会互相污染。
- 不要把 ViewModel 当作 API 请求体提交；提交前要显式构造 command / DTO。
- 不要让 ViewModel mapper 直接发请求或修改全局状态；它最好是纯函数。
- 不要把格式化后的字符串覆盖原始金额、日期或枚举；展示格式会随 locale、权限、页面而变。

**检查**：

- 领域模型类型是否只包含业务事实，而不包含页面临时状态。
- 每个页面是否有独立 ViewModel 或 mapper，而不是复用一个越来越臃肿的模型。
- ViewModel 是否由领域模型和页面 state 纯函数派生，可在单元测试中直接断言。
- 从页面提交回业务层时，是否重新构造明确的 command / DTO。
