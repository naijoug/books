# 客户端个性化首屏要先有稳定外壳

**问题**：为什么登录态、权限、主题、推荐内容或地理位置这类客户端个性化内容，不能为了“首屏准确”就在 hydration 前直接改 DOM 或让 SSR 输出和客户端首轮渲染分叉？

**要点**：

- SSR/预渲染页面的首屏外壳应该稳定：服务端 HTML 和客户端首轮渲染先匹配，再逐步补上客户端确认后的个性化内容。
- 客户端专属输入可以分成三类：服务端已有快照、客户端挂载后确认、需要用户操作后才允许读取；不要把三类混在一次渲染里。
- 个性化区域先渲染可接受的默认外壳、占位文案或 skeleton；确认后只替换局部内容，避免整页闪白。
- 如果个性化会影响布局，外壳要预留尺寸或使用 CSS 渐进增强，减少 hydration 后的布局跳动。

**示例**：

```tsx
import { useEffect, useState } from "react";

type Personalization =
  | { status: "shell" }
  | { status: "ready"; name: string; theme: "light" | "dark" };

function PersonalizedHeader({ fallbackName }: { fallbackName: string }) {
  const [personalization, setPersonalization] = useState<Personalization>({
    status: "shell",
  });

  useEffect(() => {
    const name = window.localStorage.getItem("displayName") || fallbackName;
    const storedTheme = window.localStorage.getItem("theme");
    const theme = storedTheme === "dark" ? "dark" : "light";

    setPersonalization({ status: "ready", name, theme });
  }, [fallbackName]);

  const title =
    personalization.status === "ready"
      ? `欢迎回来，${personalization.name}`
      : `欢迎，${fallbackName}`;

  const theme = personalization.status === "ready" ? personalization.theme : "light";

  return (
    <header data-theme={theme} aria-busy={personalization.status === "shell"}>
      <h1>{title}</h1>
      {personalization.status === "shell" ? <p>正在同步你的偏好设置…</p> : null}
    </header>
  );
}
```

**坑**：最常见的错误是把客户端个性化当成“要么 SSR 精准输出，要么整块不渲染”。前者容易因为 `localStorage`、浏览器主题、客户端 feature flag 或登录缓存不同而产生 hydration mismatch；后者会让首屏出现大块空白。更稳的做法是让服务端输出可接受的公共外壳，客户端挂载后只更新已经声明为个性化的局部区域。

**检查**：审查每个首屏个性化区域时，写清楚三件事：服务端能确定的默认外壳是什么；客户端确认前用户能看到的占位是否可接受；确认后替换的 DOM 是否局部、可预测、不会破坏表单输入、焦点、滚动位置和布局稳定性。
