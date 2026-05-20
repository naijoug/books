# 自定义 Hook 用来复用状态逻辑

**问题**：什么时候应该抽自定义 Hook？

**要点**：

- 多个组件共享同一套状态逻辑时抽 Hook。
- 自定义 Hook 必须以 `use` 开头。
- Hook 返回值要稳定、清晰，避免暴露内部实现细节。

**示例**：

```tsx
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : initialValue;
  });

  const update = useCallback((next: T) => {
    setValue(next);
    window.localStorage.setItem(key, JSON.stringify(next));
  }, [key]);

  return [value, update] as const;
}
```

**坑**：不要为了减少几行代码就抽 Hook。抽象应该让数据流更清晰，而不是更隐蔽。

**检查**：这个 Hook 的调用方是否不需要知道内部用了哪些 state/effect？
