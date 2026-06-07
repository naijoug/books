# Hydration 不一致要从稳定输入源治理

**问题**：为什么服务端渲染出来的页面在客户端 hydration 时会提示内容不一致，甚至导致首屏闪烁或状态丢失？

**要点**：

- Hydration 要求同一个组件在服务端首轮渲染和客户端首轮渲染时，使用同一组可序列化输入得到同一棵 DOM。
- 不要在渲染阶段直接读取 `Date.now()`、`Math.random()`、浏览器本地存储、窗口尺寸或只存在于客户端的 feature flag。
- 必须依赖环境差异的数据，要么由服务端生成快照并注入客户端首屏，要么先渲染稳定占位，再在 effect 中切换到客户端专属内容。
- `suppressHydrationWarning` 只适合少量确实不可避免的文本差异，不是修复数据来源不稳定的通用方案。

**示例**：

```tsx
import { useEffect, useState } from "react";

type InitialShell = {
  locale: string;
  renderedAtText: string;
  theme: "light" | "dark";
};

function AppShell({ initial }: { initial: InitialShell }) {
  const [theme, setTheme] = useState(initial.theme);

  useEffect(() => {
    const storedTheme = window.localStorage.getItem("theme");
    if (storedTheme === "light" || storedTheme === "dark") {
      setTheme(storedTheme);
    }
  }, []);

  return (
    <main data-locale={initial.locale} data-theme={theme}>
      <p>首屏生成时间：{initial.renderedAtText}</p>
    </main>
  );
}
```

**坑**：最常见的错误是把“客户端最终要显示什么”和“hydration 首轮必须匹配什么”混在一起。例如在 JSX 里直接写 `new Date().toLocaleString()` 或直接读 `localStorage.theme`，服务端和客户端得到的文本或属性很容易不同。正确做法是把首屏需要匹配的值作为服务端快照传入，客户端专属偏好等 hydration 完成后再更新。

**检查**：逐个审查首屏组件的渲染输入：它们是否只来自 props、服务端注入快照、稳定配置和确定性计算？凡是依赖时间、随机数、浏览器 API、网络实时结果或用户本地环境的值，都要明确放到“服务端快照”或“客户端 effect 后更新”这两个边界之一。
