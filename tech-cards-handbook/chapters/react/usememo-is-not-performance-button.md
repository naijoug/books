# `useMemo` 不是性能按钮

**问题**：是否应该给所有计算都套 `useMemo`？

**要点**：

- `useMemo` 用于缓存昂贵计算或稳定引用。
- 它本身也有成本。
- 先测量，再优化。

**示例**：

```tsx
const visibleItems = useMemo(() => {
  return items.filter((item) => item.title.includes(query));
}, [items, query]);
```

**坑**：如果 `items` 每次 render 都被重新创建，`useMemo` 仍然会重新计算。

**检查**：计算是否真的昂贵？缓存依赖是否稳定？
