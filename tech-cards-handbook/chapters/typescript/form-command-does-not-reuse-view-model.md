# 表单命令对象不要复用 ViewModel

**问题**：

表单页常把输入值、错误提示、按钮状态、脏字段、占位文案和详情页展示字段放在同一个 ViewModel 里。如果提交时直接把 ViewModel 当请求体，后端会收到 UI 临时状态；如果业务层也复用这个类型，表单验证、权限判断和展示格式会混在一起。

**要点**：

- ViewModel 服务当前界面，Command / DTO 服务一次业务动作；两者的字段边界不同。
- 表单状态可以保留 `value`、`error`、`isDirty`、`isSubmitting`，但提交前要转换成明确的 command。
- command 应只包含业务动作需要的数据，并尽量使用领域 ID、枚举、数字、布尔等未格式化类型。
- ViewModel 到 command 的 mapper 是最后一道客户端边界：在这里 trim、解析数字、丢弃 UI 字段，并返回显式错误。
- 不要让 command 依赖按钮文案、展示标签、占位文案或本地校验错误。

**示例**：

```typescript
type Brand<T, Name extends string> = T & { readonly __brand: Name };

type ProductId = Brand<string, "ProductId">;

type FieldState = {
  value: string;
  error?: string;
  isDirty: boolean;
};

type ProductEditViewModel = {
  productId: string;
  title: string;
  name: FieldState;
  priceText: FieldState;
  publishLabel: "立即发布" | "保存草稿";
  isSubmitting: boolean;
  canSubmit: boolean;
};

type UpdateProductCommand = {
  productId: ProductId;
  name: string;
  priceCents: number;
  publish: boolean;
};

type CommandResult =
  | { type: "ok"; command: UpdateProductCommand }
  | { type: "invalid"; errors: Record<"name" | "priceText", string> };

function parsePriceCents(input: string): number | null {
  const normalized = input.trim().replace(/^¥/, "");
  const amount = Number(normalized);

  if (!Number.isFinite(amount) || amount < 0) return null;
  return Math.round(amount * 100);
}

function toUpdateProductCommand(
  viewModel: ProductEditViewModel,
  publish: boolean,
): CommandResult {
  const name = viewModel.name.value.trim();
  const priceCents = parsePriceCents(viewModel.priceText.value);
  const errors: Partial<Record<"name" | "priceText", string>> = {};

  if (name.length === 0) {
    errors.name = "商品名称不能为空";
  }

  if (priceCents === null) {
    errors.priceText = "价格必须是非负数字";
  }

  if (name.length === 0 || priceCents === null) {
    return {
      type: "invalid",
      errors: errors as Record<"name" | "priceText", string>,
    };
  }

  return {
    type: "ok",
    command: {
      productId: viewModel.productId as ProductId,
      name,
      priceCents,
      publish,
    },
  };
}

const form: ProductEditViewModel = {
  productId: "product_1",
  title: "编辑商品",
  name: { value: " AI Prompt 模板手册 ", isDirty: true },
  priceText: { value: "¥99", isDirty: true },
  publishLabel: "立即发布",
  isSubmitting: false,
  canSubmit: true,
};

const result = toUpdateProductCommand(form, true);

if (result.type === "ok") {
  console.log(result.command.name, result.command.priceCents, result.command.publish);
}
```

把代码块保存为 `form-command-does-not-reuse-view-model.ts` 后，可用下面的命令做最小编译验证：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom form-command-does-not-reuse-view-model.ts
```

示例里 `ProductEditViewModel` 可以携带 `title`、`publishLabel`、`isSubmitting`、`canSubmit` 和字段脏状态；`UpdateProductCommand` 只包含一次“更新商品”动作需要的业务数据。提交边界把展示字符串解析成 `priceCents`，并把 UI 字段全部丢掉。

**坑**：

- 不要把 `FieldState`、`error`、`isDirty`、`isSubmitting` 提交给 API。
- 不要把格式化价格、日期、标签直接作为 command 字段；先解析成业务层可理解的原始值。
- 不要因为表单和详情页长得像，就复用详情页 ViewModel 作为提交类型。
- 不要只依赖按钮 disabled 状态；command mapper 仍要做必要校验并返回明确错误。

**检查**：

- command 类型是否能独立表达业务动作，不依赖页面文案或临时状态。
- ViewModel 到 command 的转换是否集中在一个纯函数中，方便单元测试。
- 提交前是否丢弃了 `error`、`isDirty`、`isSubmitting`、`label` 等 UI 字段。
- 金额、日期、枚举、ID 是否在 command 中保持业务层需要的类型，而不是展示字符串。
