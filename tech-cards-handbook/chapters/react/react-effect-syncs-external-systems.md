# React effect 同步外部系统，不处理普通计算

**问题**：什么时候需要 `useEffect`？

**要点**：

- effect 用于同步外部系统：网络、订阅、DOM、定时器、存储。
- 纯计算优先放在 render 或 `useMemo`。
- 依赖数组应该反映 effect 使用的响应式值。

**示例**：

```tsx
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then((res) => res.json())
    .then(setUser)
    .catch((error) => {
      if (error.name !== "AbortError") setError(error);
    });

  return () => controller.abort();
}, [userId]);
```

**坑**：为了消除 lint 警告随意删依赖，会让组件读到旧值。

**检查**：如果没有外部系统参与，先问自己是否真的需要 effect。
