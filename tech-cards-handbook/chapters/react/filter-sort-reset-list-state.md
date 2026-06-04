# 筛选或排序变化时重置列表状态

**问题**：无限列表支持筛选和排序后，用户快速切换条件。旧条件的下一页请求可能晚到，或者新条件沿用旧列表和旧游标，导致不同查询的数据混在一起。应该如何建模？

**要点**：

- 把筛选、排序和游标视为同一份列表查询状态；筛选或排序变化时，必须清空旧条目并把游标重置到第一页。
- 每轮加载都绑定当前 query key；响应写入前确认 key 仍然匹配，防止旧条件的结果追加到新列表。
- 能取消上一轮请求就用 `AbortController`；即使取消失败，也要用本轮身份挡住晚到响应。
- `loading`、`error`、`items`、`nextCursor` 最好集中在一个联合状态里，避免只重置一部分字段。
- 追加下一页只发生在同一个 query key 下；不要把“下一页”请求复用到新的筛选或排序条件。

**示例**：

```tsx
import { useEffect, useState } from "react";

type SortOrder = "newest" | "popular";

type Article = {
  id: string;
  title: string;
  author: string;
};

type ArticlePage = {
  items: Article[];
  nextCursor: string | null;
};

type ListState =
  | { status: "loading"; key: string; items: Article[] }
  | { status: "ready"; key: string; items: Article[]; nextCursor: string | null }
  | { status: "error"; key: string; items: Article[]; message: string };

function articleListKey(filter: string, sort: SortOrder): string {
  return `articles:${filter.trim().toLowerCase()}:${sort}`;
}

async function fetchArticles(
  filter: string,
  sort: SortOrder,
  cursor: string | null,
  signal: AbortSignal,
): Promise<ArticlePage> {
  const params = new URLSearchParams({ filter, sort });
  if (cursor !== null) params.set("cursor", cursor);

  const response = await fetch(`/api/articles?${params.toString()}`, { signal });
  if (!response.ok) {
    throw new Error(`load articles failed: ${response.status}`);
  }
  return (await response.json()) as ArticlePage;
}

export function ArticleSearch({ filter, sort }: { filter: string; sort: SortOrder }) {
  const key = articleListKey(filter, sort);
  const [state, setState] = useState<ListState>({ status: "loading", key, items: [] });

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const requestKey = articleListKey(filter, sort);

    setState({ status: "loading", key: requestKey, items: [] });

    fetchArticles(filter, sort, null, controller.signal)
      .then((page) => {
        if (!active) return;
        setState({
          status: "ready",
          key: requestKey,
          items: page.items,
          nextCursor: page.nextCursor,
        });
      })
      .catch((error: unknown) => {
        if (!active || controller.signal.aborted) return;
        const message = error instanceof Error ? error.message : "unknown error";
        setState({ status: "error", key: requestKey, items: [], message });
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [filter, sort]);

  async function loadMore() {
    if (state.status !== "ready" || state.nextCursor === null) return;

    const requestKey = key;
    const cursor = state.nextCursor;
    const controller = new AbortController();

    try {
      const page = await fetchArticles(filter, sort, cursor, controller.signal);
      setState((current) => {
        if (current.status !== "ready" || current.key !== requestKey) return current;
        return {
          status: "ready",
          key: requestKey,
          items: [...current.items, ...page.items],
          nextCursor: page.nextCursor,
        };
      });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "unknown error";
      setState((current) => {
        if (current.key !== requestKey) return current;
        return { status: "error", key: requestKey, items: current.items, message };
      });
    }
  }

  return (
    <section>
      {state.items.map((article) => (
        <article key={article.id}>
          <h3>{article.title}</h3>
          <p>{article.author}</p>
        </article>
      ))}

      {state.status === "loading" ? <p>Loading articles…</p> : null}
      {state.status === "error" ? <p role="alert">{state.message}</p> : null}
      {state.status === "ready" && state.nextCursor !== null ? (
        <button type="button" onClick={() => void loadMore()}>
          Load more
        </button>
      ) : null}
    </section>
  );
}
```

这里 `filter` 或 `sort` 变化时，首屏 effect 会立即把列表重置为空并重新加载第一页。下一页请求写入前再次检查 `current.key === requestKey`，即使旧查询的响应晚到，也不会追加到新查询的列表里。

**坑**：

- 只更新筛选条件，不清空旧列表和旧 `nextCursor`，导致新条件第一页后面接上旧条件下一页。
- 下一页请求回来后直接 `setItems([...items, ...page.items])`，没有检查响应是否仍属于当前查询。
- 把排序变化当成纯前端排序，实际接口排序和游标边界已经改变，却继续使用旧游标。
- 只处理首屏请求的 abort，忘记下一页请求也可能晚到并污染新查询。
- 用多个散落 state 分别保存 items、cursor、error，切换条件时容易漏掉其中一个。

**检查**：给列表接口加 1-2 秒延迟，连续切换筛选和排序，再点击加载更多。最终列表只能包含最后一次条件的数据；旧条件请求晚到时，不能追加旧条目，也不能沿用旧游标。