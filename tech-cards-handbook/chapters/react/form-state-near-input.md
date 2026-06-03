# 表单状态优先靠近输入

**问题**：为什么大表单一改字段就全页重渲染？

**要点**：

- 字段状态尽量靠近字段。
- 提交时再汇总数据。
- 复杂表单使用专门表单库时，也要理解校验和提交边界。

**示例**：

```tsx
function EmailField({ onValidEmail }: { onValidEmail: (email: string) => void }) {
  const [email, setEmail] = useState("");
  const isValid = email.includes("@");

  return (
    <label>
      Email
      <input
        value={email}
        onChange={(event: { target: { value: string } }) => setEmail(event.target.value)}
      />
      <button disabled={!isValid} onClick={() => onValidEmail(email)}>
        Use
      </button>
    </label>
  );
}
```

**坑**：把每个按键变化都提升到页面顶层，会让不相关区域跟着更新。

**检查**：某个状态变化时，哪些组件真的需要知道？
