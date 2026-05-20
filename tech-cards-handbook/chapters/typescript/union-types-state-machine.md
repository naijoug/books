# 用联合类型表达状态机

**问题**：为什么一个对象里同时有 `loading`、`error`、`data` 很容易出 bug？

**要点**：

- 不同状态应该互斥。
- discriminated union 让 TypeScript 帮你检查遗漏分支。
- 状态字段用固定字面量，例如 `status`。

**示例**：

```typescript
type RemoteData<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };

function renderUser(state: RemoteData<User>) {
  switch (state.status) {
    case "success":
      return state.data.name;
    case "error":
      return state.error.message;
    default:
      return null;
  }
}
```

**坑**：`data?: T` 和 `error?: Error` 会制造非法组合，例如同时有 data 和 error。

**检查**：UI 状态是否可以列成有限几种互斥状态？如果可以，用联合类型。
