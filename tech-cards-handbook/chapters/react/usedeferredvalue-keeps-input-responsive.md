# `useDeferredValue` 让输入保持响应，不阻塞在重列表上

**问题**：搜索框、筛选器或 tab 切换会触发昂贵列表渲染；用户输入一个字符，界面却因为同步重算和重绘卡住，应该怎么拆优先级？

**要点**：

- 让输入框绑定即时状态，保证每个按键立刻回显。
- 把昂贵子树读取的值改成 `useDeferredValue(value)`，让 React 可以先提交高优先级输入，再延后渲染慢列表。
- 延迟值不是防抖：它不会减少请求次数，也不会保证固定等待时间；它只是把低优先级渲染让路。
- 用 `query !== deferredQuery` 标记“结果正在追上输入”，给列表区域降透明度或显示轻量提示。
- 如果昂贵的是数据请求，仍然需要缓存、取消过期请求或服务端分页；`useDeferredValue` 只解决渲染优先级。

**示例**：

```tsx
import { useDeferredValue, useMemo, useState } from "react";

type Product = {
  id: string;
  name: string;
  description: string;
};

function ProductResults({ products, query }: { products: Product[]; query: string }) {
  const visibleProducts = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return products;
    }

    return products.filter((product) => {
      const haystack = `${product.name} ${product.description}`.toLowerCase();
      return haystack.includes(normalizedQuery);
    });
  }, [products, query]);

  return (
    <ul>
      {visibleProducts.map((product) => (
        <li key={product.id}>
          <strong>{product.name}</strong>
          <p>{product.description}</p>
        </li>
      ))}
    </ul>
  );
}

export function ProductSearch({ products }: { products: Product[] }) {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const isStale = query !== deferredQuery;

  return (
    <section>
      <label>
        搜索商品
        <input
          value={query}
          onChange={(event: { currentTarget: { value: string } }) => {
            setQuery(event.currentTarget.value);
          }}
        />
      </label>

      {isStale ? <p>结果正在更新…</p> : null}
      <div style={{ opacity: isStale ? 0.6 : 1 }}>
        <ProductResults products={products} query={deferredQuery} />
      </div>
    </section>
  );
}
```

这里输入框永远读 `query`，昂贵的 `ProductResults` 读 `deferredQuery`。当列表还没追上最新输入时，用户仍能继续打字；旧结果可以短暂保留，并用 `isStale` 给出视觉提示。

**坑**：

- 把输入框也绑定到 `deferredQuery`，会让用户看到的文本滞后。
- 把 `useDeferredValue` 当成网络防抖，结果仍然为每个输入触发请求；请求层要单独做缓存、取消和去重。
- 忘记 stale 提示，用户可能误以为旧结果就是最新结果。
- 列表本身渲染过大时，只延迟仍然会慢；应继续配合虚拟列表、分页或服务端搜索。
- 没有用 Profiler 对比同一交互，就无法判断瓶颈到底是过滤计算、DOM 数量还是网络等待。

**检查**：用 Profiler 录“连续输入 3 个字符”的交互。优化后输入框提交应更快、打字不掉帧；列表可以稍晚更新，但必须有 stale 提示，并且最终结果与直接用 `query` 过滤一致。
