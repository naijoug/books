# `unknown` 要先缩窄再使用

**问题**：当一个值来自外部输入、异常捕获或动态解析时，怎样避免把它当成任意类型直接使用？

**要点**：

- `any` 会关闭类型检查；`unknown` 会保留“不知道”的事实。
- 使用 `unknown` 后，必须先通过 `typeof`、`Array.isArray`、自定义类型守卫或 schema 校验缩窄类型。
- 适合 API 响应、`JSON.parse`、消息队列 payload、`catch` error 等边界输入。

**示例**：

```typescript
type User = {
  id: string;
  name: string;
};

function isUser(value: unknown): value is User {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const record = value as Record<string, unknown>;
  return typeof record.id === "string" && typeof record.name === "string";
}

function parseUser(payload: unknown): User {
  if (!isUser(payload)) {
    throw new Error("Invalid user payload");
  }

  return payload;
}

const raw: unknown = JSON.parse('{"id":"u1","name":"Ada"}');
const user = parseUser(raw);
console.log(user.name.toUpperCase());
```

最小验证：把上面的代码保存为 `unknown-requires-narrowing.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom unknown-requires-narrowing.ts`；如果没有类型错误，说明外部输入在进入业务使用前已完成缩窄。

**坑**：不要用 `value as User` 直接绕过 `unknown`。类型断言只会让编译器相信你，不会检查运行时数据是否真的有 `id` 和 `name`。

**检查**：凡是值来自系统边界时，先把类型写成 `unknown`；只有在完成缩窄或运行时校验后，才把它交给业务函数使用。
