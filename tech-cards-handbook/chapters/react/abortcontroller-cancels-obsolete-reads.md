# `AbortController` 取消过期读取，别让无用请求继续占资源

**问题**：用户在搜索框里连续输入、快速切换筛选条件或离开页面时，上一轮读取已经没有展示价值。如果只是在响应回来后忽略它，UI 不会被旧数据覆盖，但网络、服务端和浏览器连接仍然被占用。应该如何把“过期读取”真正取消掉？

**要点**：

- 每一轮读取创建自己的 `AbortController`，把 `signal` 传给 `fetch` 或支持取消的请求库。
- effect cleanup 中调用 `controller.abort()`，让依赖变化、组件卸载、用户主动关闭都能停止上一轮请求。
- 主动取消不是业务失败；捕获错误时先判断 `signal.aborted` 或 `error.name === "AbortError"`。
- 取消请求解决的是“资源浪费”和“无效副作用”；仍要配合本轮身份检查，防止不支持取消的库晚到回写。
- 写操作不要随便自动取消，尤其是支付、提交订单、保存表单这类有业务副作用的请求；取消更适合幂等读取。

**示例**：

```tsx
import { useEffect, useState } from "react";

type SearchResult = {
  id: string;
  title: string;
};

type SearchState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; results: SearchResult[] }
  | { status: "error"; message: string };

async function searchArticles(query: string, signal: AbortSignal): Promise<SearchResult[]> {
  const params = new URLSearchParams({ q: query });
  const response = await fetch(`/api/articles?${params.toString()}`, { signal });
  if (!response.ok) {
    throw new Error(`search failed: ${response.status}`);
  }
  return (await response.json()) as SearchResult[];
}

export function ArticleSearch({ query }: { query: string }) {
  const [state, setState] = useState<SearchState>({ status: "idle" });

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length === 0) {
      setState({ status: "idle" });
      return;
    }

    const controller = new AbortController();
    setState({ status: "loading" });

    searchArticles(trimmed, controller.signal)
      .then((results) => {
        if (controller.signal.aborted) return;
        setState({ status: "ready", results });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        const message = error instanceof Error ? error.message : "unknown error";
        setState({ status: "error", message });
      });

    return () => {
      controller.abort();
    };
  }, [query]);

  if (state.status === "idle") return <p>Type to search articles.</p>;
  if (state.status === "loading") return <p>Searching…</p>;
  if (state.status === "error") return <p role="alert">{state.message}</p>;

  return (
    <ul>
      {state.results.map((result) => (
        <li key={result.id}>{result.title}</li>
      ))}
    </ul>
  );
}
```

这里每次 `query` 变化都会清理上一轮 effect，并调用 `abort()`。快速输入 `react` 时，`r`、`re`、`rea` 等中间请求会被取消；只有最后一轮仍然有机会写入结果。catch 分支先判断 `controller.signal.aborted`，避免把主动取消展示成搜索失败。

**坑**：

- 只创建 `AbortController`，却忘了把 `signal` 传给 `fetch`，cleanup 看似执行了，实际请求仍在跑。
- 在多个请求之间复用同一个 controller；一旦调用 `abort()`，后续请求也会立刻处于 aborted 状态。
- 把 abort 错误统一记录成业务错误，导致日志和监控里充满用户快速输入造成的噪音。
- 对保存、付款、删除等写操作照搬自动取消，可能造成前端以为取消了、后端却已经处理的状态不一致。
- 认为取消请求等于缓存失效；取消只影响本轮 in-flight 请求，不会自动清理已缓存的数据。

**检查**：在浏览器 DevTools 的 Network 面板启用慢速网络，连续输入多个搜索词。旧请求应显示为 canceled/aborted 或不再继续占用连接；界面不应闪现 abort 错误，最终列表只对应最后一个搜索词。