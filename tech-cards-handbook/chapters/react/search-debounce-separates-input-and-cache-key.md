# 搜索请求防抖要分开输入值和缓存 key

## 问题

搜索框每敲一个字符就立刻请求，会把输入体验、网络请求和缓存 key 绑在一起：

- 用户输入时列表频繁闪烁。
- 同一个搜索词可能发出多次请求。
- 过短或正在编辑中的 query 进入缓存，污染后续结果。
- 慢响应晚到后覆盖更新搜索词的结果。

防抖不是为了让输入框慢下来，而是让"真正用于请求和缓存的 key"在用户暂停输入后再稳定下来。

## 要点

1. **输入值即时更新。** `inputValue` 只服务于输入框，不要因为网络请求而延迟输入。
2. **防抖后再生成请求 key。** 只有 `debouncedQuery` 达到最小长度、排序/筛选也确定后，才组成 cache key。
3. **缓存 key 必须包含影响结果的条件。** 搜索词、排序、筛选、页大小等都要进入 key；不要只用原始 query。
4. **请求前先查缓存或进行中 Promise。** 同一个 key 复用结果或复用正在飞的请求，避免重复打后端。
5. **响应写入前校验当前 key。** 防抖只能减少请求，不能保证慢响应不会晚到；写 state 前仍要确认 key 没变。

## 示例

```tsx
import { useEffect, useMemo, useRef, useState } from "react";

type SearchResult = { id: string; title: string };
type SearchState =
  | { status: "idle" }
  | { status: "loading"; key: string }
  | { status: "success"; key: string; items: SearchResult[] }
  | { status: "error"; key: string; message: string };

const resultCache = new Map<string, Promise<SearchResult[]>>();

function searchKey(query: string, sort: "relevance" | "newest") {
  return JSON.stringify({ resource: "search", query: query.trim().toLowerCase(), sort });
}

function fetchSearchResults(key: string, signal: AbortSignal) {
  const cached = resultCache.get(key);
  if (cached) return cached;

  const params = JSON.parse(key) as { query: string; sort: string };
  const promise = fetch(
    `/api/search?q=${encodeURIComponent(params.query)}&sort=${params.sort}`,
    { signal }
  )
    .then((res) => {
      if (!res.ok) throw new Error("search failed");
      return res.json() as Promise<SearchResult[]>;
    })
    .catch((error) => {
      resultCache.delete(key);
      throw error;
    });

  resultCache.set(key, promise);
  return promise;
}

function SearchPanel() {
  const [inputValue, setInputValue] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [sort, setSort] = useState<"relevance" | "newest">("relevance");
  const [state, setState] = useState<SearchState>({ status: "idle" });
  const activeKeyRef = useRef("");

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedQuery(inputValue.trim());
    }, 300);

    return () => window.clearTimeout(timer);
  }, [inputValue]);

  const key = useMemo(() => {
    if (debouncedQuery.length < 2) return "";
    return searchKey(debouncedQuery, sort);
  }, [debouncedQuery, sort]);

  useEffect(() => {
    activeKeyRef.current = key;
    if (!key) {
      setState({ status: "idle" });
      return;
    }

    const controller = new AbortController();
    setState({ status: "loading", key });

    fetchSearchResults(key, controller.signal)
      .then((items) => {
        if (activeKeyRef.current !== key) return;
        setState({ status: "success", key, items });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        if (activeKeyRef.current !== key) return;
        const message = error instanceof Error ? error.message : "unknown error";
        setState({ status: "error", key, message });
      });

    return () => controller.abort();
  }, [key]);

  return (
    <section>
      <input
        value={inputValue}
        onChange={(event: { target: { value: string } }) => setInputValue(event.target.value)}
        placeholder="Search issues"
      />
      <button type="button" onClick={() => setSort("relevance")}>Relevance</button>
      <button type="button" onClick={() => setSort("newest")}>Newest</button>
      {state.status === "loading" ? <p>Searching...</p> : null}
      {state.status === "error" ? <p role="alert">{state.message}</p> : null}
      {state.status === "success" ? (
        <ul>{state.items.map((item) => <li key={item.id}>{item.title}</li>)}</ul>
      ) : null}
    </section>
  );
}

export { SearchPanel };
```

## 最小验证命令

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx \
  search-debounce-separates-input-and-cache-key.tsx
```

## 常见坑

| 坑 | 表现 | 修正 |
|---|---|---|
| 防抖输入框本身 | 打字有延迟，用户感觉卡顿 | 输入值即时更新，只防抖请求 key |
| key 只包含 query | 切换排序后复用旧结果 | key 包含 query、sort、filter、分页参数 |
| 过短 query 也请求 | 缓存里充满无意义结果 | 低于最小长度时返回 `idle` |
| 失败 Promise 留在缓存里 | 后续同 key 永远复用失败 | `catch` 中删除缓存，让用户可重试 |
| 只做防抖不做旧响应保护 | 慢响应晚到后覆盖新结果 | 写入前比较 `activeKeyRef.current` |

## 检查清单

- [ ] 输入框状态不被防抖阻塞
- [ ] 防抖后生成稳定、可序列化的 cache key
- [ ] cache key 覆盖所有影响结果的查询条件
- [ ] 同 key 请求复用进行中 Promise 或缓存结果
- [ ] 失败后清理缓存，允许重试
- [ ] 响应写入前校验 key 仍是当前查询
