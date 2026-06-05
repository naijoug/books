# Stale-while-revalidate 保持缓存 UI，同时后台刷新

## 问题

缓存命中后如果直接显示旧数据，用户可能长期看不到最新状态；如果每次刷新都先清空 UI，又会出现加载闪烁。更好的体验是：先用缓存数据立即渲染页面，把它标记为 `stale`，同时在后台重新验证；新数据回来后再无缝替换。

## 要点

- stale-while-revalidate 适合“短暂陈旧可接受”的读取：列表、概览、推荐、搜索结果；不适合支付状态、权限判断等必须强一致的场景。
- 状态要区分 `refreshing` 和 `loading`：有缓存时刷新不应该把页面退回骨架屏。
- 后台刷新仍要防 stale response：查询条件变化或组件卸载后，旧刷新不能写回新页面。
- 失败时通常保留旧值并展示轻量错误提示，而不是把已有内容替换成失败页。
- 与 TTL/版本号配合：TTL 决定什么时候触发 revalidate，SWR 决定 revalidate 期间怎么展示。

## 示例

```tsx
import { useEffect, useState } from 'react';

type Article = { id: string; title: string; updatedAt: string };
type ArticleListState =
  | { status: 'loading' }
  | { status: 'success'; articles: Article[]; refreshing: boolean; stale: boolean; warning?: string }
  | { status: 'error'; message: string };

type ArticleCacheEntry = {
  value: Article[];
  expiresAt: number;
};

const articleCache = new Map<string, ArticleCacheEntry>();
const ARTICLE_TTL_MS = 20_000;

function cacheKey(topic: string): string {
  return `articles:${topic}`;
}

async function fetchArticles(topic: string, signal: AbortSignal): Promise<Article[]> {
  const response = await fetch(`/api/articles?topic=${encodeURIComponent(topic)}`, { signal });
  if (!response.ok) {
    throw new Error(`failed to load articles: ${response.status}`);
  }
  return response.json() as Promise<Article[]>;
}

export function ArticleList({ topic }: { topic: string }) {
  const [state, setState] = useState<ArticleListState>({ status: 'loading' });

  useEffect(() => {
    const controller = new AbortController();
    const key = cacheKey(topic);
    const cached = articleCache.get(key);
    const now = Date.now();

    if (cached) {
      setState({
        status: 'success',
        articles: cached.value,
        refreshing: cached.expiresAt <= now,
        stale: cached.expiresAt <= now,
      });
    } else {
      setState({ status: 'loading' });
    }

    if (cached && cached.expiresAt > now) {
      return () => {
        controller.abort();
      };
    }

    fetchArticles(topic, controller.signal)
      .then((articles) => {
        articleCache.set(key, { value: articles, expiresAt: Date.now() + ARTICLE_TTL_MS });
        setState({ status: 'success', articles, refreshing: false, stale: false });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return;
        }
        const message = error instanceof Error ? error.message : 'unknown error';
        if (cached) {
          setState({
            status: 'success',
            articles: cached.value,
            refreshing: false,
            stale: true,
            warning: message,
          });
        } else {
          setState({ status: 'error', message });
        }
      });

    return () => {
      controller.abort();
    };
  }, [topic]);

  if (state.status === 'loading') {
    return <p>Loading articles...</p>;
  }
  if (state.status === 'error') {
    return <p role="alert">{state.message}</p>;
  }

  return (
    <section aria-busy={state.refreshing}>
      {state.stale ? <small>Showing cached articles while refreshing.</small> : null}
      {state.warning ? <p role="status">Refresh failed: {state.warning}</p> : null}
      <ul>
        {state.articles.map((article) => (
          <li key={article.id}>{article.title}</li>
        ))}
      </ul>
    </section>
  );
}
```

## 坑

- 把后台刷新当成首屏加载，导致每次回到页面都闪骨架屏。
- 刷新失败时清空旧值，让用户从“看到旧列表”退化成“什么都没有”。
- 没有 `stale` 或 `refreshing` 标记，用户无法理解为什么页面显示旧数据。
- 对强一致数据使用 SWR，例如权限、余额、支付状态，造成风险决策基于旧值。
- 查询条件变化后复用旧 key，导致 A topic 的刷新结果写进 B topic 页面。

## 检查

- 缓存命中且未过期时，不发请求，直接渲染内容。
- 缓存过期时，旧内容保留在页面上，同时 `aria-busy` 或提示显示正在刷新。
- 刷新成功后替换为新内容，并清除 stale/refreshing 标记。
- 刷新失败但已有缓存时，页面保留旧内容并展示轻量 warning；没有缓存时才进入错误态。
- 快速切换 topic 后，旧 topic 的后台响应不会覆盖当前列表。
