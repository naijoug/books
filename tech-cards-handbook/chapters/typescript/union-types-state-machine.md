# 用联合类型表达状态机

**问题**：为什么一个对象里同时有 `loading`、`error`、`data` 很容易出 bug？

**要点**：

- 不同状态应该互斥。
- discriminated union 让 TypeScript 帮你检查遗漏分支。
- 状态字段用固定字面量，例如 `status`。

**示例**：

```typescript
type User = {
  id: string;
  name: string;
};

type RemoteData<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };

function assertNever(value: never): never {
  throw new Error(`Unhandled state: ${JSON.stringify(value)}`);
}

function renderUser(state: RemoteData<User>) {
  switch (state.status) {
    case "idle":
      return "等待加载";
    case "loading":
      return "加载中";
    case "success":
      return state.data.name;
    case "error":
      return state.error.message;
    default:
      return assertNever(state);
  }
}

const userState: RemoteData<User> = {
  status: "success",
  data: { id: "u1", name: "Ada" },
};

console.log(renderUser(userState));
```

最小验证：把上面的代码保存为 `union-types-state-machine.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom union-types-state-machine.ts`；如果没有类型错误，说明所有状态分支都已处理。可以再给 `RemoteData<T>` 增加一个 `| { status: "refreshing"; data: T }` 分支但不修改 `switch`，此时 `assertNever(state)` 会暴露未处理分支。

**坑**：`data?: T` 和 `error?: Error` 会制造非法组合，例如同时有 data 和 error；`default: return null` 也会吞掉未来新增状态，让遗漏分支在编译期不可见。

**检查**：UI 状态是否可以列成有限几种互斥状态？如果可以，用联合类型，并用 `assertNever` 让新增状态必须同步更新渲染逻辑。
