# `memo` 的收益来自稳定 props，不是无脑包裹

**问题**：为什么给子组件套了 `memo`，列表还是每次输入都整体重渲染？

**要点**：

- `memo` 只会在 props 浅比较相等时跳过子组件渲染。
- 如果父组件每次 render 都创建新的数组、对象或函数，`memo` 仍然会失效。
- 先用 React DevTools Profiler 找到真的重复渲染，再稳定传入子组件的 props。
- 稳定 props 通常来自三类动作：数据源不重复创建、派生数据用 `useMemo` 缓存、回调用 `useCallback` 或函数式更新稳定身份。

**示例**：

```tsx
import { memo, useCallback, useMemo, useState } from "react";

type Product = {
  id: string;
  name: string;
  price: number;
};

const ProductRow = memo(function ProductRow({
  product,
  selected,
  onSelect,
}: {
  key?: string;
  product: Product;
  selected: boolean;
  onSelect: (id: string) => void;
}) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={() => onSelect(product.id)}
    >
      {product.name} · ¥{product.price}
    </button>
  );
});

export function ProductTable({
  products,
  query,
}: {
  products: Product[];
  query: string;
}) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const visibleProducts = useMemo(() => {
    return products.filter((product) => product.name.includes(query));
  }, [products, query]);

  const handleSelect = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  return (
    <section>
      {visibleProducts.map((product) => (
        <ProductRow
          key={product.id}
          product={product}
          selected={product.id === selectedId}
          onSelect={handleSelect}
        />
      ))}
    </section>
  );
}
```

这里 `ProductRow` 的三个关键 props 都有清晰来源：`product` 来自父级传入的稳定列表，`selected` 是布尔值，`onSelect` 用 `useCallback` 保持身份。只有被选中状态变化影响到的行才有理由重新渲染。

**坑**：

- 在 JSX 里直接写 `onSelect={(id) => setSelectedId(id)}`，会让每一行每次都收到新函数。
- 在 render 中先 `products.map((p) => ({ ...p }))` 再传给行组件，会让每一行每次都收到新对象。
- 给廉价小组件到处包 `memo`，但没有稳定 props 或性能证据，只会增加比较成本和阅读成本。
- 为了让 `useCallback` 依赖为空而漏写真实依赖，会把稳定身份换成过期闭包。

**检查**：用 Profiler 录一次交互：哪些子组件重复渲染？它们变化的 props 是业务上真的变化，还是父组件每次新建的对象/函数？先修 props 来源，再决定是否保留 `memo`。
