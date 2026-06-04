# Profiler 先测量，再做性能优化

**问题**：页面感觉“有点卡”，应该先加 `memo`、`useMemo`，还是先定位真实瓶颈？

**要点**：

- 先用 React DevTools Profiler 或 `<Profiler>` 记录一次具体交互，再决定优化点。
- 关注 `actualDuration`：本次提交实际花了多久；再看是哪一个子树在重复渲染。
- 关注交互场景，而不是只看组件名字：输入、筛选、切 tab、打开弹窗、加载数据后的提交都可能不同。
- 优化动作要能解释测量结果：减少不必要渲染、拆分状态、稳定 props、虚拟列表或延迟重计算。
- 每次只改一个假设，改完再录同一个交互，避免把“感觉变快”当证据。

**示例**：

```tsx
import { Profiler, useState } from "react";

type Product = {
  id: string;
  name: string;
  price: number;
};

type RenderPhase = "mount" | "update" | "nested-update";

function ProductResults({ products, query }: { products: Product[]; query: string }) {
  const visibleProducts = products.filter((product) => product.name.includes(query));

  return (
    <ul>
      {visibleProducts.map((product) => (
        <li key={product.id}>
          {product.name} · ¥{product.price}
        </li>
      ))}
    </ul>
  );
}

function reportProfilerSample(sample: {
  id: string;
  phase: RenderPhase;
  actualDuration: number;
  baseDuration: number;
}) {
  console.log(
    `${sample.id} ${sample.phase}: actual=${sample.actualDuration.toFixed(1)}ms base=${sample.baseDuration.toFixed(1)}ms`,
  );
}

export function ProductSearch({ products }: { products: Product[] }) {
  const [query, setQuery] = useState("");

  return (
    <section>
      <label>
        搜索
        <input
          value={query}
          onChange={(event: { currentTarget: { value: string } }) => {
            setQuery(event.currentTarget.value);
          }}
        />
      </label>

      <Profiler
        id="product-results"
        onRender={(id, phase, actualDuration, baseDuration) => {
          reportProfilerSample({ id, phase, actualDuration, baseDuration });
        }}
      >
        <ProductResults products={products} query={query} />
      </Profiler>
    </section>
  );
}
```

先录“输入一个字符”的提交。如果 `product-results` 的 `actualDuration` 很高，再判断是过滤计算贵、列表行太多、还是每行收到新 props；然后分别考虑 `useMemo`、虚拟列表或稳定行组件 props。

**坑**：

- 没测量就全局加 `memo`，可能只增加比较成本和复杂度。
- 只看一次页面加载，不录真实交互，容易优化错场景。
- 在开发模式、热更新或 Strict Mode 下直接比较绝对耗时，可能被额外渲染干扰；更适合比较同一环境下改动前后的趋势。
- 看到某组件渲染就认为有问题；渲染本身不一定慢，慢的是昂贵计算、大列表或级联提交。
- 一次改多个变量，最后无法知道是哪一个改动真的降低了 `actualDuration`。

**检查**：写下一个可复现交互（例如“搜索框输入 3 个字符”），录优化前后的 Profiler 数据。只有当同一交互的慢子树耗时下降，且功能行为不变时，才把性能优化视为有效。
