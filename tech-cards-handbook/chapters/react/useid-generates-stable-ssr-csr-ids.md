# useId 生成跨 SSR 与 CSR 稳定的唯一 ID

**问题**：为什么 `useId` 比自增计数器或 `Math.random()` 更适合生成元素 ID？

**要点**：

- `useId` 在服务端和客户端为同一个组件生成相同的 ID，避免 SSR hydration mismatch。
- 不要把 `useId` 用作列表 key 或依赖数组值；它的设计目标是 `aria-*`、`<label htmlFor>` 等 DOM 属性。
- 自增计数器在 SSR 和 CSR 各自从 0 开始，hydration 时两端 ID 不一致会触发修复或报错。

**示例**：

```tsx
import { useId } from "react";

function FieldGroup({ label }: { label: string }) {
  const id = useId();
  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <input id={id} />
    </div>
  );
}
```

**坑**：不要在 `useEffect` 或事件处理中调用 `useId`；它必须在组件顶层调用。多个 `useId` 调用按调用顺序返回不同值，顺序不能条件化。
