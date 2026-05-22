# `useCallback` 稳定的是函数身份，不是函数执行

**问题**：什么时候应该使用 `useCallback`？

**要点**：

- `useCallback(fn, deps)` 返回一个在依赖不变时保持同一身份的函数。
- 它适合传给 `memo` 子组件、作为 Effect 依赖，或交给订阅/解绑 API。
- 它不会让函数执行更快；如果没有身份比较或依赖稳定需求，通常不需要。
- 依赖数组必须写全；若只为了少写依赖而使用空数组，容易读到过期状态。

**示例**：

```tsx
import { memo, useCallback, useState } from "react";

type Todo = {
  id: string;
  title: string;
  done: boolean;
};

const TodoRow = memo(function TodoRow({
  todo,
  onToggle,
}: {
  todo: Todo;
  onToggle: (id: string) => void;
}) {
  return (
    <label>
      <input
        type="checkbox"
        checked={todo.done}
        onChange={() => onToggle(todo.id)}
      />
      {todo.title}
    </label>
  );
});

export function TodoList({ initialTodos }: { initialTodos: Todo[] }) {
  const [todos, setTodos] = useState(initialTodos);

  const handleToggle = useCallback((id: string) => {
    setTodos((current) =>
      current.map((todo) =>
        todo.id === id ? { ...todo, done: !todo.done } : todo,
      ),
    );
  }, []);

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          <TodoRow todo={todo} onToggle={handleToggle} />
        </li>
      ))}
    </ul>
  );
}
```

上面 `TodoRow` 被 `memo` 包裹，会比较 props 身份。`handleToggle` 使用函数式更新，因此不依赖当前 `todos`，可以安全保持稳定身份。

**坑**：

- 把所有事件处理函数都包一层 `useCallback`，但子组件没有 `memo`，也没有把函数放进依赖数组或订阅 API，通常只是增加阅读成本。
- 为了让依赖数组为空而漏写 `userId`、`query`、`config` 等真实依赖，会造成闭包读取旧值。
- 如果回调依赖一个每次 render 都新建的对象，`useCallback` 仍然会跟着失效；先稳定对象来源，或把对象拆成必要的原始依赖。

**检查**：这个函数身份是否真的被比较、缓存、订阅或作为 Effect 依赖？依赖数组是否能通过 `eslint-plugin-react-hooks` 检查？如果删除 `useCallback` 后没有额外渲染或重复订阅问题，就不要保留它。
