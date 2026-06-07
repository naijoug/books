# 浏览器 API 读取放到客户端挂载之后

**问题**：为什么在 React SSR 或静态预渲染页面里，直接读取 `window`、`document`、`localStorage`、媒体查询或窗口尺寸，容易导致构建失败、hydration 不一致或首屏闪烁？

**要点**：

- 服务端渲染阶段没有浏览器环境，渲染函数必须能在没有 `window` 和 `document` 的地方执行。
- 首屏 HTML 要用稳定默认值或服务端快照生成；客户端专属信息等挂载后再读取。
- 浏览器 API 读取通常放进 `useEffect`，并用局部状态从“未知/默认”过渡到“客户端确认值”。
- 如果这个值会影响布局，先设计一个稳定占位或 CSS 兜底，避免挂载后大幅跳动。

**示例**：

```tsx
import { useEffect, useState } from "react";

type ColorScheme = "light" | "dark";

function ThemePreview({ serverTheme }: { serverTheme: ColorScheme }) {
  const [theme, setTheme] = useState<ColorScheme>(serverTheme);

  useEffect(() => {
    const query = window.matchMedia("(prefers-color-scheme: dark)");

    function syncTheme() {
      setTheme(query.matches ? "dark" : "light");
    }

    syncTheme();
    query.addEventListener("change", syncTheme);
    return () => query.removeEventListener("change", syncTheme);
  }, []);

  return <section data-theme={theme}>当前主题：{theme}</section>;
}
```

**坑**：常见错误是在组件渲染体里直接写 `window.innerWidth`、`document.body.dataset.theme` 或 `localStorage.getItem("theme")`。这会让组件只能在浏览器里跑；一旦进入 SSR、预渲染、测试或 React Server Components 周边环境，就可能因为环境不存在而崩溃。即使加了 `typeof window !== "undefined"`，也可能让服务端首屏和客户端首轮渲染拿到不同值。

**检查**：搜索首屏组件里的 `window`、`document`、`localStorage`、`matchMedia`、`ResizeObserver` 和 `navigator`。凡是出现在渲染阶段的读取，都要问三件事：服务端是否能执行；客户端首轮是否和服务端输出一致；挂载后更新是否有稳定占位、清理函数和可接受的视觉变化。
