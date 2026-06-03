# 乐观更新必须有回滚路径

**问题**：

用户点击“新增”“点赞”“归档”后，如果界面一直等服务器返回才变化，会显得迟钝；但如果只做乐观更新，不设计失败回滚，网络错误、权限失败或服务端校验失败时，本地 UI 会显示一条根本不存在的数据。

**要点**：

- 乐观更新适合用户意图明确、失败概率低、结果容易撤销的操作。
- 先给本地数据加临时身份，例如 `clientId`，服务器成功后再替换成真实记录。
- 失败时必须回滚本次变更，并把错误交给调用方显示 toast、inline error 或重试入口。
- pending 状态要按操作或临时 ID 跟踪，不要只用一个全局 `isSaving` 阻塞整个列表。
- 服务端返回如果会重排、补字段或合并数据，应以服务端结果为准，而不是长期保留乐观对象。

**示例**：

```tsx
type Todo = {
  id: string;
  title: string;
  completed: boolean;
  optimistic?: boolean;
};

declare function createTodo(input: { title: string }): Promise<Todo>;

export function useOptimisticTodos(initialTodos: Todo[]) {
  const [todos, setTodos] = useState(initialTodos);
  const [pendingIds, setPendingIds] = useState<Set<string>>(() => new Set());

  async function addTodo(title: string) {
    const clientId = `client-${Date.now()}`;
    const optimisticTodo: Todo = {
      id: clientId,
      title,
      completed: false,
      optimistic: true,
    };

    setTodos((currentTodos) => [optimisticTodo, ...currentTodos]);
    setPendingIds((currentIds) => new Set(currentIds).add(clientId));

    try {
      const savedTodo = await createTodo({ title });
      setTodos((currentTodos) =>
        currentTodos.map((todo) => (todo.id === clientId ? savedTodo : todo)),
      );
    } catch (error) {
      setTodos((currentTodos) => currentTodos.filter((todo) => todo.id !== clientId));
      throw error;
    } finally {
      setPendingIds((currentIds) => {
        const nextIds = new Set(currentIds);
        nextIds.delete(clientId);
        return nextIds;
      });
    }
  }

  return { todos, pendingIds, addTodo };
}
```

最小验证：把上面的代码保存为 `optimistic-update-with-rollback.tsx`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx --lib es2020,dom optimistic-update-with-rollback.tsx`。测试时至少覆盖两条路径：`createTodo` resolve 后临时 ID 被替换；`createTodo` reject 后临时记录被移除，错误仍能被上层捕获。

**坑**：

- 只在成功路径替换数据，失败时什么都不做，导致刷新前 UI 一直撒谎。
- 用数组索引定位乐观项；列表排序、筛选或并发新增后会回滚错对象。
- 多个请求共用一个 `isSaving`，导致一个 item pending 时整页按钮都被禁用。
- 在 catch 里吞掉错误，用户看不到失败，也无法选择重试。
- 服务端成功后仍保留 `optimistic: true` 或临时 ID，后续更新会找不到真实记录。

**检查**：

- 每个乐观操作是否都有成功替换和失败回滚两条路径？
- 是否用稳定临时 ID 追踪本次操作，而不是靠数组位置？
- 并发触发两次操作时，pending 状态和回滚是否只影响对应项？
- 服务端返回和本地乐观对象冲突时，最终是否以服务端结果为准？
