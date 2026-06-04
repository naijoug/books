# `startTransition` 标记非紧急更新，让输入和导航先响应

**问题**：一次点击或输入同时更新“当前输入/选中项”和“大列表/图表/路由内容”。如果所有状态都按同一优先级同步渲染，用户会感觉输入卡顿或导航迟迟没有反馈，应该如何拆优先级？

**要点**：

- 紧急状态直接更新：输入框内容、按钮选中态、导航高亮这些必须马上反馈。
- 非紧急的昂贵更新放进 `startTransition(() => setState(...))`，让 React 可以先提交紧急反馈，再继续渲染慢子树。
- 用 `useTransition()` 拿到 `isPending` 和 `startTransition`；`isPending` 适合在慢区域显示“正在更新”，不要把整个页面锁死。
- transition 不会让计算变快，也不会自动取消网络请求；它只是降低渲染优先级。昂贵计算仍要配合 memo、虚拟列表、分页或缓存。
- 不要把受控输入的 `setInputValue` 放进 transition，否则输入显示也会被延后。

**示例**：

```tsx
import { useMemo, useState, useTransition } from "react";

type Issue = {
  id: string;
  title: string;
  status: "open" | "closed";
};

function IssueList({ issues, status }: { issues: Issue[]; status: Issue["status"] }) {
  const visibleIssues = useMemo(() => {
    return issues.filter((issue) => issue.status === status);
  }, [issues, status]);

  return (
    <ul>
      {visibleIssues.map((issue) => (
        <li key={issue.id}>{issue.title}</li>
      ))}
    </ul>
  );
}

export function IssueStatusTabs({ issues }: { issues: Issue[] }) {
  const [selectedStatus, setSelectedStatus] = useState<Issue["status"]>("open");
  const [listStatus, setListStatus] = useState<Issue["status"]>("open");
  const [isPending, startTransition] = useTransition();

  function selectStatus(nextStatus: Issue["status"]) {
    setSelectedStatus(nextStatus); // 紧急：tab 高亮立即切换。
    startTransition(() => {
      setListStatus(nextStatus); // 非紧急：大列表可以稍后追上。
    });
  }

  return (
    <section>
      <button
        aria-pressed={selectedStatus === "open"}
        onClick={() => selectStatus("open")}
      >
        Open
      </button>
      <button
        aria-pressed={selectedStatus === "closed"}
        onClick={() => selectStatus("closed")}
      >
        Closed
      </button>

      {isPending ? <p>列表正在切换…</p> : null}
      <div style={{ opacity: isPending ? 0.6 : 1 }}>
        <IssueList issues={issues} status={listStatus} />
      </div>
    </section>
  );
}
```

这里 tab 高亮读 `selectedStatus`，所以点击后立即变化；大列表读 `listStatus`，它在 transition 中更新，可以让慢渲染稍后追上。`isPending` 只提示列表区域正在更新，不阻塞继续点击。

**坑**：

- 把受控输入的 `setQuery` 或 tab 高亮的 `setSelectedStatus` 放进 transition，导致用户最需要的反馈也变慢。
- 以为 transition 会节省计算量；如果列表一次渲染上万行，仍然要做虚拟列表、分页或服务端过滤。
- 用全屏 loading 覆盖 transition，反而把“可继续交互”的优势抹掉。
- transition 内发起网络请求但没有缓存和过期处理，旧请求仍可能晚到覆盖新状态。
- 没有用 Profiler 对比交互，只凭感觉给所有更新套 `startTransition`。

**检查**：用 Profiler 录制“快速切换两个 tab”的交互。优化后 tab 高亮应立即响应，慢列表允许延后，并且 pending 提示只覆盖慢区域；最终列表内容必须与最后一次选中的 tab 一致。
