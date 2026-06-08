# 外部 API 响应先过 schema 边界

**问题**：调用第三方 API、后端接口或 agent 工具时，返回值看起来像 `User`，但运行时可能缺字段、字段类型变了、状态枚举新增了。怎样避免错误 payload 悄悄流进业务逻辑？

**要点**：

- `fetch().json()`、工具结果和消息队列 payload 在类型上都先当成 `unknown`，不要直接 `as DomainType`。
- 在系统边界写一个 schema/decoder 函数：负责运行时检查、默认值、字段重命名和错误信息。
- decoder 的返回类型优先使用 `Result<T, E>`，让调用方显式处理“格式不符合预期”。
- 业务函数只接收已经通过 decoder 的领域对象；这样 agent 或维护者能清楚看到可信数据从哪里开始。
- schema 边界可以手写，也可以替换成 Zod、Valibot、ArkType 等库；核心不是库，而是“边界必须验证”。

**示例**：

```typescript
type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

type ApiUser = {
  id: string;
  email: string;
  plan: "free" | "pro";
  createdAt: Date;
};

type DecodeError = {
  field: string;
  message: string;
};

function ok<T>(value: T): Result<T, DecodeError> {
  return { ok: true, value };
}

function err(field: string, message: string): Result<ApiUser, DecodeError> {
  return { ok: false, error: { field, message } };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function decodeApiUser(payload: unknown): Result<ApiUser, DecodeError> {
  if (!isRecord(payload)) {
    return err("root", "expected object");
  }

  if (typeof payload.id !== "string" || payload.id.length === 0) {
    return err("id", "expected non-empty string");
  }

  if (typeof payload.email !== "string" || !payload.email.includes("@")) {
    return err("email", "expected email string");
  }

  if (payload.plan !== "free" && payload.plan !== "pro") {
    return err("plan", "expected free or pro");
  }

  if (typeof payload.created_at !== "string") {
    return err("created_at", "expected ISO date string");
  }

  const createdAt = new Date(payload.created_at);
  if (Number.isNaN(createdAt.getTime())) {
    return err("created_at", "expected valid date");
  }

  return ok({
    id: payload.id,
    email: payload.email,
    plan: payload.plan,
    createdAt,
  });
}

async function loadUser(response: Response): Promise<Result<ApiUser, DecodeError>> {
  const payload: unknown = await response.json();
  return decodeApiUser(payload);
}

function renderUser(user: ApiUser): string {
  return `${user.email} joined at ${user.createdAt.toISOString()}`;
}

async function renderUserFromApi(response: Response): Promise<string> {
  const result = await loadUser(response);
  if (!result.ok) {
    return `API 响应格式错误：${result.error.field} ${result.error.message}`;
  }

  return renderUser(result.value);
}
```

最小验证：把上面的代码保存为 `external-api-response-schema-boundary.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom external-api-response-schema-boundary.ts`；如果没有类型错误，说明业务函数只接收 schema 边界验证后的 `ApiUser`。

**坑**：不要把 `await response.json() as ApiUser` 当成验证。`as` 只改变 TypeScript 的静态视角，不会检查运行时字段；接口一旦返回 `{ created_at: null }` 或新增未知枚举，错误会在更远的业务逻辑里爆炸。

**检查**：每个外部输入边界都问四件事：原始 payload 是否先是 `unknown`？是否有独立 decoder/schema？decoder 是否返回可处理的错误？业务函数是否完全不依赖未验证字段？
