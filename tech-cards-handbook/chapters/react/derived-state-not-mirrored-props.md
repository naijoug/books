# 派生状态不要镜像 props

**问题**：

组件经常需要从 props 或已有 state 里计算出筛选结果、计数、展示标签或是否可提交。把这些值再塞进 `useState`，再用 Effect 同步，容易出现两份数据不同步：props 变了但派生 state 没更新，或者用户操作触发了中间帧的旧结果。

**要点**：

- 能从当前 props/state 直接算出来的值，优先在渲染阶段计算，而不是复制成新的 state。
- 只有用户可以独立修改、需要跨渲染保留、或不能从现有输入重新推导的值，才应该放进 state。
- 计算便宜时直接算；计算昂贵且输入稳定时，用 `useMemo` 缓存计算结果。
- 不要用 Effect 做“props 变化后 setState 同步派生值”，这会制造额外渲染和短暂不一致。
- 真正需要“初始化后可编辑”的场景，要把它命名成 draft/local state，并明确什么时候重置。

**示例**：

```tsx
import { useMemo } from "react";

type Product = {
  id: string;
  name: string;
  category: string;
  price: number;
};

type ProductListProps = {
  products: Product[];
  selectedCategory: string | null;
  maxPrice: number;
};

export function ProductList({
  products,
  selectedCategory,
  maxPrice,
}: ProductListProps) {
  const visibleProducts = useMemo(() => {
    return products.filter((product) => {
      const categoryMatches =
        selectedCategory === null || product.category === selectedCategory;
      return categoryMatches && product.price <= maxPrice;
    });
  }, [products, selectedCategory, maxPrice]);

  const resultLabel = `${visibleProducts.length} products found`;

  return (
    <section>
      <p>{resultLabel}</p>
      <ul>
        {visibleProducts.map((product) => (
          <li key={product.id}>{product.name}</li>
        ))}
      </ul>
    </section>
  );
}
```

这里 `visibleProducts` 和 `resultLabel` 都由当前输入推导出来。它们不需要单独的 `useState`，因此不会出现“筛选条件已经变了，但列表仍显示旧派生结果”的中间状态。

**坑**：

- `const [visibleProducts, setVisibleProducts] = useState(products)` 然后在 Effect 里同步：首帧会拿到旧值，还多一次渲染。
- 把 `props.user.name` 复制到 `name` state，却没有定义“外部 user 变化时是否覆盖用户正在编辑的草稿”。
- 为了避免重复计算滥用 `useMemo`：如果只是几个布尔判断或轻量字符串拼接，直接计算更简单。
- 在派生值里偷偷写副作用，例如统计上报、缓存写入或修改外部对象；渲染阶段计算必须保持纯函数。

**检查**：

- 这个 state 是否可以完全由当前 props、URL 参数、缓存数据或其他 state 推导出来？如果可以，先删掉它。
- 删除派生 state 后，是否仍能通过一次渲染得到正确 UI，而不依赖 Effect 追赶同步？
- 如果保留 local/draft state，是否写清楚初始化来源、用户编辑边界和重置时机？
- 对昂贵派生计算，是否只在输入稳定且 Profiler 显示有成本时使用 `useMemo`？
