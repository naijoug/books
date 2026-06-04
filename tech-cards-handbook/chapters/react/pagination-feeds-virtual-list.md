# 分页负责数据边界，虚拟列表负责渲染窗口

**问题**：接口已经分页了，前端还需要虚拟列表吗？或者用了虚拟列表后，是否可以一次把所有数据都拉到浏览器？

**要点**：

- 分页和虚拟列表解决的是两个不同问题：分页控制网络与内存边界，虚拟列表控制同时渲染的 DOM 数量。
- 分页状态应该围绕服务端游标、已加载条目和是否还有下一页建模，不要把它绑死到当前滚动窗口。
- 虚拟窗口只从“已加载数据”里切可见区；接近已加载尾部时再触发下一页读取。
- 触发下一页前要有 `loadingMore` 护栏，避免滚动事件连续打出重复请求。
- 不要用窗口起止索引当分页参数；筛选、排序或插入数据后，索引会漂移，服务端游标更稳。

**示例**：

```tsx
import { useMemo, useState } from "react";

type Activity = {
  id: string;
  title: string;
  actor: string;
};

type Page = {
  items: Activity[];
  nextCursor: string | null;
};

const ROW_HEIGHT = 56;
const VIEWPORT_HEIGHT = 360;
const OVERSCAN = 6;
const LOAD_MORE_THRESHOLD = 8;

async function fetchActivities(cursor: string | null): Promise<Page> {
  const search = cursor ? `?cursor=${encodeURIComponent(cursor)}` : "";
  const response = await fetch(`/api/activities${search}`);
  if (!response.ok) {
    throw new Error(`load activities failed: ${response.status}`);
  }
  return (await response.json()) as Page;
}

function ActivityRow({ activity }: { key?: string; activity: Activity }) {
  return (
    <article style={{ height: ROW_HEIGHT }}>
      <strong>{activity.actor}</strong> {activity.title}
    </article>
  );
}

export function ActivityFeed({ initialPage }: { initialPage: Page }) {
  const [items, setItems] = useState<Activity[]>(initialPage.items);
  const [nextCursor, setNextCursor] = useState<string | null>(initialPage.nextCursor);
  const [scrollTop, setScrollTop] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const windowState = useMemo(() => {
    const firstVisible = Math.floor(scrollTop / ROW_HEIGHT);
    const visibleCount = Math.ceil(VIEWPORT_HEIGHT / ROW_HEIGHT);
    const start = Math.max(0, firstVisible - OVERSCAN);
    const end = Math.min(items.length, firstVisible + visibleCount + OVERSCAN);

    return {
      end,
      topPadding: start * ROW_HEIGHT,
      bottomPadding: (items.length - end) * ROW_HEIGHT,
      visibleItems: items.slice(start, end),
    };
  }, [items, scrollTop]);

  async function loadMoreIfNeeded(lastVisibleIndex: number) {
    const shouldLoad =
      nextCursor !== null &&
      !loadingMore &&
      lastVisibleIndex >= items.length - LOAD_MORE_THRESHOLD;

    if (!shouldLoad) return;

    setLoadingMore(true);
    setError(null);
    try {
      const page = await fetchActivities(nextCursor);
      setItems((current) => [...current, ...page.items]);
      setNextCursor(page.nextCursor);
    } catch (unknownError: unknown) {
      const message = unknownError instanceof Error ? unknownError.message : "unknown error";
      setError(message);
    } finally {
      setLoadingMore(false);
    }
  }

  return (
    <section>
      <div
        style={{ height: VIEWPORT_HEIGHT, overflow: "auto" }}
        onScroll={(event: { currentTarget: { scrollTop: number } }) => {
          const nextScrollTop = event.currentTarget.scrollTop;
          setScrollTop(nextScrollTop);
          const lastVisibleIndex = Math.ceil((nextScrollTop + VIEWPORT_HEIGHT) / ROW_HEIGHT);
          void loadMoreIfNeeded(lastVisibleIndex);
        }}
      >
        <div style={{ height: windowState.topPadding }} />
        {windowState.visibleItems.map((activity) => (
          <ActivityRow key={activity.id} activity={activity} />
        ))}
        <div style={{ height: windowState.bottomPadding }} />
      </div>

      {loadingMore ? <p>Loading more…</p> : null}
      {error ? <p role="alert">{error}</p> : null}
    </section>
  );
}
```

这个组件只渲染已加载数据中的可见窗口；当滚动接近已加载尾部时，用服务端返回的 `nextCursor` 拉下一页。分页边界和渲染窗口互不替代：接口仍然按页返回，DOM 仍然只保留几十行。

**坑**：

- 以为“接口分页了”就能安全渲染已加载的几千行，结果 DOM 提交仍然很慢。
- 以为“虚拟列表了”就可以一次拉全量数据，结果首包、内存和缓存都失控。
- 用 `start` / `end` 这类窗口索引请求服务端数据，筛选或插入后会加载错页。
- 没有 `loadingMore` 护栏，滚到底部时滚动事件连续触发多次相同请求。
- 只追加数据但不处理筛选条件变化；筛选变化时应清空旧列表、重置游标并防止旧响应回写。

**检查**：在 10000 条数据场景下观察三件事：Network 每次只请求下一页且没有重复请求；Performance/Profiler 中同时渲染的行数保持在视口窗口附近；快速切换筛选或排序时不会把旧条件的下一页追加到新列表。