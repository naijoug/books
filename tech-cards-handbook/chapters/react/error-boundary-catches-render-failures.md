# Error Boundary 捕获渲染失败，不捕获事件失败

**问题**：为什么一个子组件 render 抛错后整棵 React 树都白屏？

**要点**：

- Error Boundary 用来把局部渲染失败隔离在一小块 UI 内。
- 它捕获子组件在 render、生命周期和构造阶段抛出的错误。
- 它不捕获事件处理器、异步回调、服务端渲染和自身内部抛出的错误。
- 边界要放在“可以独立降级”的区域，例如侧栏、卡片列表、图表或插件面板。

**示例**：

```tsx
import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = {
  children: ReactNode;
  fallback?: ReactNode;
};

type State = {
  hasError: boolean;
};

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    reportRenderError(error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? <p>这个区域暂时不可用。</p>;
    }

    return this.props.children;
  }
}

function Dashboard() {
  return (
    <main>
      <ErrorBoundary fallback={<p>图表加载失败。</p>}>
        <RevenueChart />
      </ErrorBoundary>
      <RecentOrders />
    </main>
  );
}
```

事件处理器里的错误要在事件内处理，而不是依赖 Error Boundary：

```tsx
function SaveButton() {
  async function handleClick() {
    try {
      await saveDraft();
    } catch (error) {
      showToast("保存失败，请稍后重试");
    }
  }

  return <button onClick={handleClick}>保存</button>;
}
```

**坑**：只在应用最外层放一个 Error Boundary，虽然能避免整页崩溃，但用户只能看到一个大 fallback；太细地给每个小组件都套边界，又会让降级 UI 变碎。边界粒度应跟产品可独立恢复的区域一致。

**检查**：页面里哪些区域失败后可以单独显示 fallback？这些区域的事件失败和异步失败是否另有错误处理？
