# 手动重试把错误恢复交还给用户

## 问题

自动重试可以覆盖短暂网络抖动，但不能无限替用户做决定。连续失败后，界面需要进入可理解、可恢复的错误态：告诉用户失败原因，保留仍可用的旧数据，并提供一个明确的“重试”入口。手动重试的价值不是多发一次请求，而是把失败恢复从后台策略变成用户可控动作。

## 要点

- 自动重试到达上限后，状态要停在 `error` 或 `success + warning`，而不是继续静默轮询。
- 手动重试应重新发起当前 key 的请求；如果查询条件已变化，重试的是新条件，不是旧条件。
- 有旧数据时不要清空页面：重试期间用 `retrying` 或 `aria-busy` 标记，让内容继续可读。
- 重试按钮要防重复点击：请求进行中禁用按钮，或用并发锁忽略重复触发。
- 错误文案要区分“可重试的读取失败”和“需要用户修改输入/权限”的失败。

## 示例

```tsx
import { useEffect, useState } from 'react';

type Report = { id: string; title: string; score: number };
type ReportState =
  | { status: 'loading' }
  | { status: 'success'; report: Report; retrying: boolean; warning?: string }
  | { status: 'error'; message: string; retrying: boolean };

async function fetchReport(reportId: string, signal: AbortSignal): Promise<Report> {
  const response = await fetch(`/api/reports/${reportId}`, { signal });
  if (!response.ok) {
    throw new Error(`failed to load report: ${response.status}`);
  }
  return response.json() as Promise<Report>;
}

export function ReportPanel({ reportId }: { reportId: string }) {
  const [state, setState] = useState<ReportState>({ status: 'loading' });
  const [retryToken, setRetryToken] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    setState((current) => {
      if (current.status === 'success') {
        return { ...current, retrying: true, warning: undefined };
      }
      if (current.status === 'error') {
        return { ...current, retrying: true };
      }
      return { status: 'loading' };
    });

    fetchReport(reportId, controller.signal)
      .then((report) => {
        setState({ status: 'success', report, retrying: false });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return;
        }
        const message = error instanceof Error ? error.message : 'unknown error';
        setState((current) => {
          if (current.status === 'success') {
            return { ...current, retrying: false, warning: message };
          }
          return { status: 'error', message, retrying: false };
        });
      });

    return () => {
      controller.abort();
    };
  }, [reportId, retryToken]);

  const retry = () => {
    setRetryToken((token) => token + 1);
  };

  if (state.status === 'loading') {
    return <p>Loading report...</p>;
  }

  if (state.status === 'error') {
    return (
      <section aria-busy={state.retrying}>
        <p role="alert">{state.message}</p>
        <button type="button" disabled={state.retrying} onClick={retry}>
          {state.retrying ? 'Retrying...' : 'Retry'}
        </button>
      </section>
    );
  }

  return (
    <section aria-busy={state.retrying}>
      {state.warning ? <p role="status">Refresh failed: {state.warning}</p> : null}
      <h2>{state.report.title}</h2>
      <p>Score: {state.report.score}</p>
      <button type="button" disabled={state.retrying} onClick={retry}>
        {state.retrying ? 'Retrying...' : 'Retry'}
      </button>
    </section>
  );
}
```

## 坑

- 失败后只显示错误文案，没有按钮或下一步，用户只能刷新整个页面。
- 点击重试时清空已有内容，导致用户从“有旧数据”退化成“空白加载”。
- 重试按钮不禁用，连续点击触发多次相同请求，又引入竞态问题。
- 手动重试仍使用旧闭包里的查询条件，筛选条件变化后请求错对象。
- 把所有失败都包装成“请重试”，掩盖权限不足、参数非法等用户需要改输入的错误。

## 检查

- 首次加载失败时页面显示 `role="alert"` 的错误信息和可点击的重试按钮。
- 有旧数据时刷新失败，旧数据仍保留，只显示轻量 warning。
- 重试进行中按钮禁用，并通过 `aria-busy` 标记区域正在恢复。
- 快速切换 `reportId` 后，旧请求被取消，旧响应不会覆盖新报表。
- 达到自动重试上限后，系统停在可操作错误态，而不是无限静默重试。
