# `React.lazy` 优先切路由和重模块，不要随机拆小组件

**问题**：把很多小组件都改成 `React.lazy` 后，为什么首屏没有明显变快，反而出现更多闪烁和加载边界？

**要点**：

- `React.lazy` 适合拆“低频进入的大块”：路由页、设置页、图表编辑器、富文本编辑器、管理后台模块。
- 不要为了“看起来做了性能优化”拆每个按钮、卡片和小组件；过多 chunk 会增加网络往返、边界嵌套和维护成本。
- 每个 lazy 组件必须有就近的 Suspense fallback，fallback 要匹配该区域大小，避免布局跳动。
- lazy 只解决代码下载时机，不解决数据请求失败；需要时仍要配合 Error Boundary。

**示例**：

```tsx
import { lazy, Suspense, type ComponentType } from "react";

type ReportPageProps = {
  accountId: string;
};

declare function loadReportPage(): Promise<{
  default: ComponentType<ReportPageProps>;
}>;

const ReportPage = lazy(loadReportPage);

function ReportsRoute({ accountId }: { accountId: string }) {
  return (
    <Suspense fallback={<main aria-busy="true">正在加载报表模块...</main>}>
      <ReportPage accountId={accountId} />
    </Suspense>
  );
}
```

**坑**：把 `lazy` 放进组件函数内部会在每次渲染时创建新的组件类型，导致状态丢失和重复加载判断；应该像示例一样放在模块顶层。另一个坑是只拆一个非常小的展示组件，却没有拆真正沉重的依赖，结果多了异步边界但没有减少首屏关键代码。

**检查**：这个 lazy chunk 是否对应一个可独立等待的产品区域？fallback 是否不会让布局明显跳动？如果模块加载失败，是否有上层 Error Boundary 给出可恢复 UI？
