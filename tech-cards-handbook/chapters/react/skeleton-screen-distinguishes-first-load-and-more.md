# 骨架屏要区分首屏加载和加载更多

## 问题

列表的"加载中"状态只有一种，会导致：

- 首屏加载时骨架屏闪一下就消失，用户分不清是空还是还在加载。
- 加载更多时整个列表被骨架屏替换，已看过的内容跳动。
- 首屏空状态和首屏加载态无法区分，`[]` 空结果和 `undefined` 未加载展示一样。
- 加载更多失败后没有提示，用户不知道已经到底还是出错了。

正确做法是把加载状态分成首屏（整个骨架屏）和追加（底部 spinner），并用空状态兜底。

## 要点

1. **首屏用骨架屏或占位。** 列表还没有任何数据时，展示与实际布局接近的骨架行，而不是全屏 spinner。
2. **加载更多用底部 spinner。** 已有数据时，在列表底部追加一行加载指示器，不影响已渲染内容。
3. **空状态只在首屏成功后展示。** 首屏请求成功且结果为空时才展示空状态；加载中和加载更多失败都不应展示空状态。
4. **加载更多失败要有重试。** 底部提示加载失败并提供重试按钮，不要静默吞掉错误。
5. **状态类型覆盖四个阶段。** `idle` → `loadingFirst` → `loaded` → `loadingMore`，不合并为单一 `loading` 布尔。

## 示例

```tsx
import { useCallback, useRef, useState } from "react";

type Item = { id: string; title: string };

type ListPhase =
  | { status: "idle" }
  | { status: "loadingFirst" }
  | { status: "loaded"; items: Item[]; hasMore: boolean }
  | { status: "loadingMore"; items: Item[]; hasMore: boolean }
  | { status: "errorMore"; items: Item[]; hasMore: boolean; message: string };

function ItemRow({ item }: { item: Item }) {
  return <li>{item.title}</li>;
}

function SkeletonRow({ index }: { index: number }) {
  return <li aria-hidden="true">{"placeholder " + index}</li>;
}

function ItemList() {
  const [phase, setPhase] = useState<ListPhase>({ status: "idle" });
  const cursorRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const loadFirst = useCallback(() => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    cursorRef.current = null;
    setPhase({ status: "loadingFirst" });

    fetch("/api/items?limit=10", { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error("first load failed");
        return res.json() as Promise<{ items: Item[]; nextCursor: string | null }>;
      })
      .then((data) => {
        if (controller.signal.aborted) return;
        cursorRef.current = data.nextCursor;
        setPhase({ status: "loaded", items: data.items, hasMore: data.nextCursor !== null });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        const message = error instanceof Error ? error.message : "unknown error";
        setPhase({ status: "errorMore", items: [], hasMore: false, message });
      });
  }, []);

  const loadMore = useCallback(() => {
    if (phase.status !== "loaded" && phase.status !== "errorMore") return;
    if (!phase.hasMore) return;

    const controller = new AbortController();
    abortRef.current = controller;
    setPhase({ status: "loadingMore", items: phase.items, hasMore: phase.hasMore });

    const cursor = cursorRef.current;
    fetch(`/api/items?limit=10&cursor=${encodeURIComponent(cursor ?? "")}`, {
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error("load more failed");
        return res.json() as Promise<{ items: Item[]; nextCursor: string | null }>;
      })
      .then((data) => {
        if (controller.signal.aborted) return;
        cursorRef.current = data.nextCursor;
        setPhase({
          status: "loaded",
          items: [...phase.items, ...data.items],
          hasMore: data.nextCursor !== null,
        });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        const message = error instanceof Error ? error.message : "unknown error";
        setPhase({ status: "errorMore", items: phase.items, hasMore: phase.hasMore, message });
      });
  }, [phase]);

  if (phase.status === "idle" || phase.status === "loadingFirst") {
    return (
      <section>
        <ul>
          {Array.from({ length: 5 }, (_, i) => (
            <SkeletonRow key={i} index={i} />
          ))}
        </ul>
      </section>
    );
  }

  if (phase.status === "loaded" && phase.items.length === 0) {
    return <p>No items found.</p>;
  }

  const items = phase.items;
  const isLoadingMore = phase.status === "loadingMore";
  const errorMore = phase.status === "errorMore" ? phase.message : null;
  const hasMore = phase.hasMore;

  return (
    <section>
      <ul>
        {items.map((item) => (
          <ItemRow key={item.id} item={item} />
        ))}
      </ul>
      {isLoadingMore ? <p>Loading more...</p> : null}
      {errorMore ? (
        <p role="alert">
          {errorMore} <button onClick={loadMore}>Retry</button>
        </p>
      ) : null}
      {!isLoadingMore && !errorMore && hasMore ? (
        <button onClick={loadMore}>Load more</button>
      ) : null}
    </section>
  );
}

export { ItemList };
```

## 最小验证命令

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx \
  skeleton-screen-distinguishes-first-load-and-more.tsx
```

## 常见坑

| 坑 | 表现 | 修正 |
|---|---|---|
| 首屏和加载更多共用 `loading` | 加载更多时列表被骨架屏替换 | 用 `ListPhase` 联合类型区分四个阶段 |
| 空状态在加载中也展示 | 数据还没到就显示"无结果" | 空状态只在 `loaded` + `items.length === 0` 时展示 |
| 加载更多失败无提示 | 用户以为已到底 | `errorMore` 状态展示错误信息和重试按钮 |
| 骨架屏与实际行高度不一致 | 加载完成后内容跳动 | 骨架屏使用与 `ItemRow` 接近的高度和间距 |
| 不取消旧请求 | 快速触发加载更多导致竞态 | 每次加载创建新 `AbortController`，取消旧请求 |

## 检查清单

- [ ] 首屏加载展示骨架屏或占位
- [ ] 加载更多展示底部 spinner，不替换已有内容
- [ ] 空状态只在首屏成功后、结果为空时展示
- [ ] 加载更多失败有错误提示和重试
- [ ] 状态类型覆盖 idle / loadingFirst / loaded / loadingMore / errorMore
