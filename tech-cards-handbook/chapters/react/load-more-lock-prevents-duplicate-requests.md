# 加载更多时必须有并发锁，防止重复请求和重复追加

## 问题

"加载更多"按钮或滚动到底部自动加载时，如果用户快速点击或在请求完成前再次触发，会同时发出多个相同的下一页请求。每个响应都会追加到列表，导致：

- 重复条目出现在列表中。
- 分页游标跳过实际页。
- 服务端因突发重复请求而负载升高。

`loading` 布尔值不够——它只反映"有没有请求在飞"，不能阻止组件在 React 批处理或异步竞争中多次进入加载路径。

## 要点

1. **用布尔锁而不是计数器。** 加载更多只有两种合法状态：空闲和进行中。不需要同时飞两个下一页请求。
2. **锁必须在函数入口设置，而不是在状态更新后。** `setLoading(true)` 是异步的——在它生效前，其他渲染周期可能已经读过旧的 `loading` 值。
3. **请求失败后释放锁。** 用 `try/finally` 而不是 `try/catch` 保证锁一定被清除，即使网络错误或解析失败。
4. **`AbortController` 与锁配合使用。** 锁防止新请求，`AbortController` 取消正在飞的旧请求——例如筛选条件变化时需要立刻放弃当前加载更多。
5. **响应写入前仍然校验 query key。** 即使有锁，组件卸载或筛选变化后旧响应仍可能到达。在追加数据前检查查询是否仍然是当前查询。

## 示例

```tsx
import { useState, useCallback, useRef } from "react";

interface ListState {
  items: Array<{ id: string; title: string }>;
  nextCursor: string | null;
}

function usePagedList(baseUrl: string) {
  const [state, setState] = useState<ListState>({
    items: [],
    nextCursor: "",
  });
  const [loadingMore, setLoadingMore] = useState(false);
  const loadingRef = useRef(false);
  const abortRef = useRef<AbortController | null>(null);
  const queryKeyRef = useRef("");

  const loadMore = useCallback(async () => {
    if (loadingRef.current) return;
    if (state.nextCursor === null) return;

    loadingRef.current = true;
    setLoadingMore(true);

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const currentKey = queryKeyRef.current;

    try {
      const url = `${baseUrl}?cursor=${state.nextCursor}`;
      const res = await fetch(url, { signal: controller.signal });
      const data: { items: Array<{ id: string; title: string }>; nextCursor: string | null } =
        await res.json();

      if (queryKeyRef.current !== currentKey) return;

      setState((prev) => ({
        items: [...prev.items, ...data.items],
        nextCursor: data.nextCursor,
      }));
    } catch (err) {
      if (controller.signal.aborted) return;
      console.error("load more failed", err);
    } finally {
      loadingRef.current = false;
      setLoadingMore(false);
    }
  }, [baseUrl, state.nextCursor]);

  const resetQuery = useCallback(
    (newKey: string) => {
      queryKeyRef.current = newKey;
      abortRef.current?.abort();
      loadingRef.current = false;
      setLoadingMore(false);
      setState({ items: [], nextCursor: "" });
    },
    []
  );

  return { state, loadingMore, loadMore, resetQuery };
}

export { usePagedList };
```

## 最小验证命令

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx \
  load-more-lock-prevents-duplicate-requests.tsx
```

## 常见坑

| 坑 | 表现 | 修正 |
|---|---|---|
| 用 `loading` state 做锁 | React 批处理下 state 未更新，多个调用同时通过 | 改用 `useRef` 布尔锁 |
| 忘记 `finally` 释放锁 | 请求失败后永远不能再次加载更多 | 用 `try/finally` 而不是 `try/catch` |
| 不取消旧请求 | 切换筛选后旧请求的响应仍然追加到新列表 | `AbortController` 配合 `resetQuery` |
| 追加前不校验 query key | 快速切换筛选后，旧查询的下一页覆盖新列表 | 写入前比较 `queryKeyRef.current` |
| 锁与分页游标不一致 | 锁释放了但游标仍指向旧位置 | `resetQuery` 同时清锁、游标和列表 |

## 检查清单

- [ ] 加载更多函数入口用 `useRef` 布尔锁防重入
- [ ] 锁在 `finally` 中释放
- [ ] 有 `AbortController` 可以取消正在飞的请求
- [ ] 响应写入前校验查询是否仍是当前查询
- [ ] 已到最后一页（`nextCursor === null`）时不再触发加载
- [ ] 筛选/排序变化时调用 `resetQuery` 同时清锁、游标和列表
