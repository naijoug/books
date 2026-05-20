# `useState` 更新依赖旧值时用函数式更新

**问题**：为什么连续点击或异步回调里读到的 state 可能是旧的？

**要点**：

- `setState(next)` 使用当前 render 闭包里的值。
- `setState(prev => next)` 使用 React 提供的最新前值。
- 初始化很贵时，用惰性初始化函数。

**示例**：

```tsx
const [count, setCount] = useState(0);

function increment() {
  setCount((prevCount) => prevCount + 1);
}

const [data] = useState(() => expensiveComputation());
```

**坑**：把不相关字段都塞进一个大 state 对象，更新时容易漏字段，也会扩大重渲染范围。

**检查**：这个更新是否依赖旧 state？依赖就用函数式更新。
