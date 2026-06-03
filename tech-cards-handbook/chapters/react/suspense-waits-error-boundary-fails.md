# Suspense 处理等待，Error Boundary 处理失败

**问题**：异步组件加载中和加载失败都用一个 `loading` 状态处理，为什么 UI 不是一直转圈，就是失败后整块崩掉？

**要点**：

- Suspense 只负责“还没准备好”的等待状态，用 `fallback` 展示骨架屏或占位。
- Error Boundary 负责“已经失败”的错误状态，用 fallback 展示可恢复的降级 UI。
- 两者通常成对出现：外层 Error Boundary 接住失败，内层 Suspense 接住等待。
- 边界要包住一个产品上可独立恢复的区域，不要把全站唯一边界当成所有异步 UI 的答案。

**示例**：

```tsx
import { Component, Suspense, type ErrorInfo, type ReactNode } from "react";

type BoundaryProps = {
  children: ReactNode;
  fallback: ReactNode;
};

type BoundaryState = {
  hasError: boolean;
};

class ErrorBoundary extends Component<BoundaryProps, BoundaryState> {
  state: BoundaryState = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    reportRenderError(error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}

function UserInsights() {
  return (
    <section>
      <h2>用户洞察</h2>
      <ErrorBoundary fallback={<p>洞察加载失败，请稍后重试。</p>}>
        <Suspense fallback={<p>正在加载洞察骨架屏...</p>}>
          <RevenueChart />
        </Suspense>
      </ErrorBoundary>
    </section>
  );
}
```

**坑**：把 Error Boundary 放在 Suspense 里面，仍然可以捕获子树渲染错误，但失败 fallback 会替换 Suspense 内部区域；如果产品希望“等待”和“失败”都共享同一个区域边界，通常把 Error Boundary 放外层更直观。另一个常见坑是只写 Suspense fallback，却没有错误边界：请求失败后不会自动变成 loading，而是继续向上抛错。

**检查**：异步区域是否分别定义了“等待时看到什么”和“失败时看到什么”？失败 fallback 是否给出重试、返回或稍后再试等可恢复路径？
