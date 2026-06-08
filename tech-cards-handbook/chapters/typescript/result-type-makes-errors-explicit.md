# Result 类型让错误处理显式

## 问题

`throw` 和 `try/catch` 很容易把可恢复错误藏起来：调用方只看到一个 `Promise<User>`，却不知道网络失败、权限不足、字段校验失败分别该怎么处理。业务代码继续往下写时，错误路径会散落在日志、toast 和兜底 `catch` 里，最后变成“失败了就弹一段通用文案”。

对于预期内、需要调用方分支处理的错误，可以把返回值写成 `Result<T, E>`：成功和失败都在类型里，调用方必须先缩窄再取数据。

## 要点

- `Result<T, E>` 适合表达**可恢复、可预期、需要业务分支处理**的失败，例如表单校验、权限不足、库存不足、远端接口返回业务错误。
- `throw` 仍适合表达**程序员错误或不可恢复异常**，例如配置缺失、违反不变量、JSON schema 与代码版本完全不匹配。
- 错误类型 `E` 不要只写成 `string`；用 discriminated union 保留 `type`、字段名、状态码、可展示消息和可观测信息。
- 调用方先判断 `ok`，再读取 `value` 或 `error`；不要把 `Result` 立刻 unwrap 成异常，否则又回到隐式错误路径。
- 组合多个 `Result` 时，可以写小的 `map` / `andThen` 帮助函数，但项目早期先保持显式 `if (!result.ok)`，更容易读懂业务分支。

## 示例

```ts
type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

type User = {
  id: string;
  email: string;
};

type CreateUserError =
  | { type: "invalid_email"; field: "email"; message: string }
  | { type: "duplicate_email"; field: "email"; message: string }
  | { type: "network"; retryAfterMs: number; message: string };

function ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

function err<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

async function createUser(email: string): Promise<Result<User, CreateUserError>> {
  if (!email.includes("@")) {
    return err({
      type: "invalid_email",
      field: "email",
      message: "邮箱格式不正确",
    });
  }

  const response = await fakeCreateUserRequest(email);

  if (response.status === 409) {
    return err({
      type: "duplicate_email",
      field: "email",
      message: "这个邮箱已经注册过",
    });
  }

  if (!response.ok) {
    return err({
      type: "network",
      retryAfterMs: 1000,
      message: "网络异常，请稍后重试",
    });
  }

  return ok(response.user);
}

async function submit(email: string): Promise<string> {
  const result = await createUser(email);

  if (!result.ok) {
    switch (result.error.type) {
      case "invalid_email":
      case "duplicate_email":
        return `字段 ${result.error.field}: ${result.error.message}`;
      case "network":
        return `${result.error.message}，建议 ${result.error.retryAfterMs}ms 后重试`;
      default:
        return assertNever(result.error);
    }
  }

  return `创建成功: ${result.value.email}`;
}

function assertNever(value: never): never {
  throw new Error(`Unhandled error branch: ${JSON.stringify(value)}`);
}

async function fakeCreateUserRequest(email: string): Promise<
  | { ok: true; status: 201; user: User }
  | { ok: false; status: 409 | 500 }
> {
  if (email === "exists@example.com") {
    return { ok: false, status: 409 };
  }

  return {
    ok: true,
    status: 201,
    user: { id: "user_1", email },
  };
}
```

## 坑

- **把所有异常都塞进 Result**：磁盘损坏、代码不变量被破坏、依赖版本不兼容这类不可恢复异常不一定适合变成业务返回值。
- **错误只用字符串**：`Result<T, string>` 会让调用方只能做文案展示，不能稳定区分字段错误、权限错误和可重试错误。
- **过早 unwrap**：写一个 `unwrap(result)` 失败就 throw，会抹掉 `Result` 带来的显式分支价值。
- **错误 union 不做穷尽检查**：新增错误类型后，如果调用方没有 `assertNever` 或等价穷尽检查，很容易漏掉 UI 分支。
- **把库边界和业务边界混在一起**：底层 HTTP client 可以返回通用网络错误，但业务 service 应该把它翻译成调用方看得懂的领域错误。

## 检查

- 函数签名是否能直接看出“会成功返回什么、会失败返回什么”。
- 每个预期内错误是否有稳定 `type`，而不是只靠 message 文案判断。
- 调用方是否必须先判断 `ok` 才能读取 `value`。
- 新增一个错误分支时，`switch` 是否会被 TypeScript 或 `assertNever` 推到需要修改。
- 日志、toast、字段错误和重试按钮是否能从 `error.type` 推导出来，而不是在多个 `catch` 里重复猜测。
