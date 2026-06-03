# 异步状态用联合类型表达，不用多个布尔值

**问题**：

页面里经常同时出现 `isLoading`、`error`、`data`、`isRefreshing` 等状态。它们分散在多个 `useState` 里时，很容易组合出不可能的 UI：既在 loading 又有 error，已经 success 但 data 为空，或者请求失败后旧数据和错误提示互相覆盖。

**要点**：

- 把异步流程建模成一个 discriminated union：`idle`、`loading`、`success`、`error` 等状态互斥。
- UI 根据 `state.status` 渲染，避免多个布尔值互相打架。
- 状态转移集中放在 reducer 或自定义 Hook 里，不要在组件各处散落 `setLoading(false)`、`setError(null)`。
- 如果需要保留旧数据刷新，可以显式建模 `refreshing`，而不是用 `isLoading && data` 这种隐式组合。
- 和 TypeScript 的 `never` 穷尽检查配合，新增状态时让编译器提醒你补 UI 分支。

**示例**：

```typescript
// 文档示例为了便于单文件类型检查，写出 useReducer 的最小类型签名；
// 实际项目中应从 React 导入：import { useReducer } from "react"。
declare function useReducer<State, Action>(
  reducer: (state: State, action: Action) => State,
  initialState: State,
): [State, (action: Action) => void];

type AsyncState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; message: string };

type Action<T> =
  | { type: "start" }
  | { type: "resolve"; data: T }
  | { type: "reject"; message: string }
  | { type: "reset" };

function assertNever(value: never): never {
  throw new Error(`unhandled async action: ${JSON.stringify(value)}`);
}

function asyncReducer<T>(state: AsyncState<T>, action: Action<T>): AsyncState<T> {
  switch (action.type) {
    case "start":
      return { status: "loading" };
    case "resolve":
      return { status: "success", data: action.data };
    case "reject":
      return { status: "error", message: action.message };
    case "reset":
      return { status: "idle" };
    default:
      return assertNever(action);
  }
}

export function useAsyncUser() {
  const [state, dispatch] = useReducer(asyncReducer<{ id: string; name: string }>, {
    status: "idle",
  });

  async function loadUser(userId: string) {
    dispatch({ type: "start" });
    try {
      const response = await fetch(`/api/users/${userId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = (await response.json()) as { id: string; name: string };
      dispatch({ type: "resolve", data });
    } catch (error) {
      const message = error instanceof Error ? error.message : "unknown error";
      dispatch({ type: "reject", message });
    }
  }

  return { state, loadUser, reset: () => dispatch({ type: "reset" }) };
}

export function describeUserPanel(state: AsyncState<{ id: string; name: string }>): string {
  switch (state.status) {
    case "idle":
      return "请选择用户";
    case "loading":
      return "加载中...";
    case "success":
      return `用户：${state.data.name}`;
    case "error":
      return `加载失败：${state.message}`;
    default:
      return assertNever(state);
  }
}
```

最小验证：把上面的代码保存为 `async-state-discriminated-union.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom async-state-discriminated-union.ts`。如果给 `AsyncState` 新增 `| { status: "empty" }` 但不修改 `describeUserPanel`，`assertNever(state)` 会让编译器报错。

**坑**：

- 用 `const [loading, setLoading]`、`const [error, setError]`、`const [data, setData]` 分开维护同一条异步链路，最后会出现 impossible state。
- 在请求开始时忘记清空旧错误，或者在失败时忘记关闭 loading；集中 reducer 可以减少这类遗漏。
- 用 `as AsyncState<T>` 强行断言后绕过状态建模，相当于把问题推迟到运行时。
- 只处理成功和失败，不考虑 `idle` 或取消/重试状态，组件初始渲染时会出现空白或闪烁。

**检查**：

- 组件渲染是否只依赖一个 `state.status`，而不是多个布尔值组合？
- 每个异步动作是否都有明确的状态转移：开始、成功、失败、重置？
- 新增一个状态后，UI 分支、按钮可用性和文案是否都会被 TypeScript 提醒同步更新？
- 是否需要把“刷新中但保留旧数据”建模成独立状态，而不是偷偷复用 `loading`？
