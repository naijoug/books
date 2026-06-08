# DTO 边界不要泄漏领域模型

**问题**：

领域模型通常包含内部状态、审计字段、权限信息或后端专用标记。如果 API 响应、前端 props、消息队列事件直接复用领域模型，外部消费者会看到不该依赖的字段；一旦领域模型重构，所有边界调用方都会被迫跟着变。

**要点**：

- 领域模型是内部事实，DTO 是边界契约；两者不要用同一个类型名、同一个对象直接穿透。
- 输出 DTO 应只暴露调用方需要的字段，并把内部枚举、Date、品牌 ID 等转换成稳定格式。
- 输入 DTO 应先经过 decoder / mapper 转成领域命令，再交给业务逻辑。
- mapper 函数是显式边界：字段增删、脱敏、格式转换和版本兼容都集中在这里。
- 可以用 `Pick` / `Omit` 派生简单 DTO，但最终仍应通过 `toXxxDto` / `fromXxxDto` 固化边界含义。

**示例**：

```typescript
type Brand<T, Name extends string> = T & { readonly __brand: Name };

type UserId = Brand<string, "UserId">;

type Account = {
  id: UserId;
  email: string;
  displayName: string;
  passwordHash: string;
  role: "admin" | "member";
  billingPlan: "free" | "pro";
  deletedAt: Date | null;
  createdAt: Date;
};

type PublicAccountDto = {
  id: string;
  displayName: string;
  plan: "free" | "pro";
  joinedAt: string;
};

type AdminAccountDto = PublicAccountDto & {
  email: string;
  role: "admin" | "member";
  isDeleted: boolean;
};

function toPublicAccountDto(account: Account): PublicAccountDto {
  return {
    id: account.id,
    displayName: account.displayName,
    plan: account.billingPlan,
    joinedAt: account.createdAt.toISOString(),
  };
}

function toAdminAccountDto(account: Account): AdminAccountDto {
  return {
    ...toPublicAccountDto(account),
    email: account.email,
    role: account.role,
    isDeleted: account.deletedAt !== null,
  };
}

type UpdateProfileDto = {
  displayName: string;
};

type UpdateProfileCommand = {
  accountId: UserId;
  displayName: string;
};

function fromUpdateProfileDto(
  accountId: UserId,
  dto: UpdateProfileDto,
): UpdateProfileCommand {
  const displayName = dto.displayName.trim();

  if (displayName.length < 2) {
    throw new Error("displayName must contain at least 2 characters");
  }

  return { accountId, displayName };
}

const account: Account = {
  id: "user_1" as UserId,
  email: "ada@example.com",
  displayName: "Ada",
  passwordHash: "sha256:internal-only",
  role: "admin",
  billingPlan: "pro",
  deletedAt: null,
  createdAt: new Date("2026-01-01T00:00:00.000Z"),
};

const publicDto = toPublicAccountDto(account);
const adminDto = toAdminAccountDto(account);
const command = fromUpdateProfileDto(account.id, { displayName: " Ada Lovelace " });

console.log(publicDto.id, publicDto.joinedAt, adminDto.email, command.displayName);
```

把代码块保存为 `dto-boundary-hides-domain-model.ts` 后，可用下面的命令做最小编译验证：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom dto-boundary-hides-domain-model.ts
```

注意 `PublicAccountDto` 没有 `passwordHash`、`role`、`deletedAt`，也没有把 `Date` 和品牌类型原样暴露给外部。外部只看到稳定字符串和业务需要字段。

**坑**：

- 不要把 `Account` 直接作为 controller 返回值、React props 或事件 payload；它迟早会泄漏内部字段。
- 不要让 DTO 反向污染领域模型：为了前端展示临时加的 `isSelected`、`label`、`href` 应留在 view model，不要塞进领域类型。
- 不要只靠 `Omit<Account, "passwordHash">` 就认为安全；后续新增内部字段时仍可能被自动暴露。
- DTO mapper 不应偷偷访问数据库或发请求；它只做纯字段转换和边界校验。

**检查**：

- 每个外部边界是否都有明确的 `Dto` / `Command` / `Event` 类型，而不是复用领域模型。
- 输出 mapper 是否集中处理脱敏、字段重命名、`Date` 序列化和品牌类型降级。
- 输入 mapper 是否在进入业务层前完成 trim、基本校验和领域命令构造。
- 领域模型新增敏感字段时，是否不会自动出现在公开 DTO 中。
