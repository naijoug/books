# `useRef` 保存可变值但不触发重渲染

**问题**：哪些值应该放 ref，而不是 state？

**要点**：

- DOM 节点引用适合 ref。
- timer id、上一次值、外部实例句柄适合 ref。
- 需要影响 UI 的值不要只放 ref。

**示例**：

```tsx
function usePrevious<T>(value: T) {
  const ref = useRef<T>();

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
}
```

**坑**：修改 `ref.current` 不会触发 render。UI 需要更新时仍然要用 state。

**检查**：这个值变化后，界面是否应该立即变化？是的话不要只用 ref。
