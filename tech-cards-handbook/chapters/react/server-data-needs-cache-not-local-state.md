# 服务端数据用缓存层管理，不复制到组件 state

**问题**：

从接口拿回来的列表、详情、用户信息经常被直接 `setData(result)` 存进组件 state。一旦多个组件都要读同一份数据，或者某个提交需要让其他页面的旧数据失效，开发者就在组件之间手动同步 state，或者在 Effect 里反复请求同一接口。结果要么数据不一致（A 组件更新了，B 组件还显示旧值），要么请求泛滥（每个挂载都发起一次 fetch）。

**要点**：

- 服务端数据只有一个可靠来源：请求缓存。组件应该从缓存读取，而不是各自维护一份本地副本。
- 缓存层负责：去重（同一个 key 的并发请求合并）、失效（mutation 成功后标记旧数据过期）、过期（TTL 到期后重新请求）。
- 本地 state 只存当前编辑中的草稿、表单输入、UI 开关等纯客户端瞬时状态。
- 如果项目暂时不上库，最小实现可以用 `Map<string, { data; promise; updatedAt }>` 搭配自定义 Hook 完成；不需要一步到位选 React Query。
- 缓存 key 通常由 URL + 参数对象决定，而不是组件实例决定。

**示例**：

```tsx
import { useState, useEffect, useCallback, useRef } from "react";

type CacheEntry<T> = {
  data: T;
  updatedAt: number;
};

const cache = new Map<string, CacheEntry<unknown>>();
const inflight = new Map<string, Promise<unknown>>();

function readCache<T>(key: string): T | null {
  const entry = cache.get(key);
  return entry !== undefined ? (entry.data as T) : null;
}

function useFetch<T>(key: string, fetcher: () => Promise<T>, ttlMs: number) {
  const [state, setState] = useState<{ status: "pending" | "ok"; data: T | null }>({
    status: "pending",
    data: readCache<T>(key),
  });
  const mountedRef = useRef(true);

  useEffect(() => {
    const cached = readCache<T>(key);
    if (cached !== null && Date.now() - (cache.get(key)!.updatedAt) < ttlMs) {
      setState({ status: "ok", data: cached });
      return;
    }

    let promise = inflight.get(key) as Promise<T> | undefined;
    if (promise === undefined) {
      promise = fetcher().then((data) => {
        cache.set(key, { data, updatedAt: Date.now() });
        inflight.delete(key);
        return data;
      });
      inflight.set(key, promise);
    }

    promise.then(
      (data) => { if (mountedRef.current) setState({ status: "ok", data }); },
      () => { if (mountedRef.current) setState({ status: "ok", data: null }); },
    );

    return () => { mountedRef.current = false; };
  }, [key, ttlMs]);

  return state;
}

export function useInvalidate(keyPrefix: string) {
  return useCallback(() => {
    const keysToDelete: string[] = [];
    for (const k of Array.from(cache.keys())) {
      if (k.startsWith(keyPrefix)) keysToDelete.push(k);
    }
    keysToDelete.forEach((k) => cache.delete(k));
  }, [keyPrefix]);
}
```

组件通过 `useFetch("products:list", fetcher, 60_000)` 读取数据，提交后通过 `useInvalidate("products:")` 让缓存失效；下次渲染自动重新请求。数据不在任何组件 state 里，多组件自然共享同一份缓存。

**坑**：

- 把接口返回值 `setData(result)` 放进组件 state，然后在另一个组件里用 Effect 轮询或事件总线同步：越同步越不一致。
- 在每个组件挂载时都发请求，同一页面三个组件用同一个接口数据就发了三次。
- 手写缓存但没有去重：三个组件同时挂载，三个请求同时飞出，前两个的结果被第三个覆盖。
- 缓存 key 只包含 URL 不包含筛选参数：切换筛选条件时读到的还是上一组参数的数据。
- 不设置过期时间：用户已经在另一个终端修改了数据，本地缓存永远不更新。

**检查**：

- 接口返回的数据是否只存在缓存层，而不是散落在多个组件的 `useState` 里？
- 多个组件同时挂载时，同一个接口是否只发一次请求（去重）？
- 提交/删除成功后，相关缓存是否被正确失效，而不是靠页面刷新？
- 缓存 key 是否完整包含了影响返回结果的所有参数？
- 是否有合理的过期策略，避免用户长期停留在旧数据上？
