# Error Boundary 的重试需要重置失败子树

**问题**：页面已经用 Error Boundary 接住了渲染错误，为什么用户点“重试”后还是停在失败界面，或者旧的错误状态一直残留？

**要点**：

- Error Boundary 捕获错误后会进入自己的失败状态；重试时必须显式清掉这个状态。
- 如果失败来自子组件内部缓存、懒加载模块或数据读取器，只重置边界状态可能不够，还要用 `key` 重新挂载失败子树。
- 重试按钮要放在 fallback 里，触发“边界 state reset + 子树 key 变化 + 重新请求/重新读取”的闭环。
- 边界粒度应对应可独立恢复的产品区域，例如一个图表、一张订单卡片或一个设置面板。

**示例**：

```tsx
import { Component, Suspense, useState, type ErrorInfo, type ReactNode } from "react";

type RetryBoundaryProps = {
  children: ReactNode;
  fallback: (retry: () => void) => ReactNode;
  onRetry?: () => void;
};

type RetryBoundaryState = {
  hasError: boolean;
};

class RetryBoundary extends Component<RetryBoundaryProps, RetryBoundaryState> {
  state: RetryBoundaryState = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    reportRenderError(error, info.componentStack);
  }

  retry = () => {
    this.props.onRetry?.();
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      return this.props.fallback(this.retry);
    }

    return this.props.children;
  }
}

function RevenuePanel() {
  const [attempt, setAttempt] = useState(0);

  return (
    <RetryBoundary
      onRetry={() => setAttempt((current) => current + 1)}
      fallback={(retry) => (
        <section role="alert">
          <p>收入图表加载失败。</p>
          <button type="button" onClick={retry}>重试</button>
        </section>
      )}
    >
      <Suspense fallback={<p>正在加载收入图表...</p>}>
        <RevenueChart key={String(attempt)} />
      </Suspense>
    </RetryBoundary>
  );
}
```

**坑**：只在 fallback 中写一个“重试”按钮，但按钮只重新发请求、不清除 Error Boundary 的 `hasError`，界面仍然停在 fallback；反过来，只清除边界状态但没有让失败子树重新挂载或重新读取，也可能再次拿到旧错误。另一个坑是把整个应用包在一个全局重试边界里，导致局部图表失败时需要重置整页。

**检查**：失败 fallback 是否有明确重试入口？点击重试时是否同时清除边界错误状态、触发子树重新读取或重新挂载？边界是否足够小，能让用户只恢复出错区域而不是刷新整页？
