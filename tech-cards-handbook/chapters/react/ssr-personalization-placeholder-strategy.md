# SSR 个性化首屏要有渐进占位策略

**问题**：服务端渲染的页面包含个性化区域（主题、权限、推荐内容、地理位置）时，如何让首屏既不空白也不 hydration mismatch，还能在客户端确认后平滑过渡到真实内容？

**要点**：

- 占位策略分三层：骨架层（高度/尺寸稳定的内容轮廓）、降级层（可接受的公共默认内容）、真实层（客户端确认后的个性化内容）。三层依次呈现，不要从空白直接跳到真实内容。
- 骨架层的尺寸必须在 SSR 时确定：用 CSS 固定高度、`aspect-ratio` 或 `min-height`，不能依赖客户端计算的尺寸，否则 hydration 后会触发布局偏移（CLS）。
- 降级层使用服务端已知的公共数据：未登录时显示通用欢迎词、默认主题、通用推荐列表；关键是降级层本身不读取任何浏览器 API。
- 真实层替换时机是客户端 Effect 确认后：通过 discriminated union 状态（`"skeleton" | "fallback" | "personalized"`）控制，替换时只更新内部文本或切换 CSS class，不增减 DOM 节点。
- 个性化区域的边界要显式声明：用 `aria-busy`、`aria-live="polite"` 或 `data-personalized` 属性标记，方便测试和辅助技术识别过渡状态。

**示例**：

```tsx
import { useEffect, useState } from "react";

type ThemePreference = "light" | "dark";

type PersonalizedState =
  | { phase: "skeleton" }
  | { phase: "fallback"; theme: ThemePreference }
  | { phase: "personalized"; theme: ThemePreference; greeting: string };

function WelcomeSection({ serverName }: { serverName: string }) {
  const [state, setState] = useState<PersonalizedState>({ phase: "skeleton" });

  useEffect(() => {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme: ThemePreference = prefersDark ? "dark" : "light";

    setState({ phase: "fallback", theme });

    const storedName = window.localStorage.getItem("userName");
    if (storedName) {
      setState({ phase: "personalized", theme, greeting: `欢迎回来，${storedName}` });
    } else {
      setState({ phase: "personalized", theme, greeting: `你好，${serverName}` });
    }
  }, [serverName]);

  return (
    <section
      data-theme={state.phase === "skeleton" ? "light" : state.theme}
      aria-busy={state.phase !== "personalized"}
      aria-live="polite"
      style={{ minHeight: 120 }}
    >
      {state.phase === "skeleton" && (
        <div className="skeleton-line" style={{ height: 24, width: "60%" }} />
      )}
      {state.phase === "fallback" && <h2>你好，{serverName}</h2>}
      {state.phase === "personalized" && <h2>{state.greeting}</h2>}
    </section>
  );
}
```

**坑**：最常见的错误是把占位策略简化成"先渲染 null，Effect 里再 setState"——这会让 SSR 输出空节点，客户端 hydration 后突然出现内容，既产生 CLS 又让屏幕阅读器用户困惑。另一个常见坑是在降级层就读取 `matchMedia` 或 `localStorage`，导致 SSR 和客户端首轮渲染不一致。正确做法是骨架层只输出固定尺寸的占位结构，降级层只用服务端已知数据，真实层才替换为客户端确认后的内容。

**检查**：审查每个 SSR 个性化区域时，确认三件事：骨架层是否有固定尺寸且不依赖浏览器 API；降级层是否只使用服务端已知数据；真实层替换时是否只更新内容而不增减 DOM 节点。如果任何一层跳过，说明占位策略不完整，用户会看到闪烁、跳动或空白。
