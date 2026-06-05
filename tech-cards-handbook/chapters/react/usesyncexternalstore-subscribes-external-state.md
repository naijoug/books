# useSyncExternalStore 订阅外部状态源

**问题**：为什么订阅浏览器、全局 store 或第三方数据源时，不建议只用 `useEffect` + `useState` 手写同步？

**要点**：

- `useSyncExternalStore` 把“订阅变化”和“读取当前快照”拆开，让 React 在并发渲染中读到一致的外部状态。
- `getSnapshot` 必须是纯读取；同一份外部状态没有变化时要返回同一个值，避免无限重渲染。
- SSR 场景要提供 `getServerSnapshot`，否则服务端首屏和客户端 hydration 可能读到不同初值。
- 它适合浏览器 API、Redux/Zustand 这类外部 store、WebSocket 缓存等“React 之外拥有状态”的来源；组件内部状态仍然用 `useState`/`useReducer`。

**示例**：

```tsx
import { useSyncExternalStore } from "react";

type Theme = "light" | "dark";

const listeners = new Set<() => void>();
let currentTheme: Theme = "light";

export const themeStore = {
  getSnapshot() {
    return currentTheme;
  },
  getServerSnapshot() {
    return "light" as Theme;
  },
  subscribe(listener: () => void) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  setTheme(nextTheme: Theme) {
    if (nextTheme === currentTheme) return;
    currentTheme = nextTheme;
    listeners.forEach((listener) => listener());
  },
};

function ThemeBadge() {
  const theme = useSyncExternalStore(
    themeStore.subscribe,
    themeStore.getSnapshot,
    themeStore.getServerSnapshot,
  );

  return <span>Theme: {theme}</span>;
}
```

**坑**：不要在 `getSnapshot` 里创建新对象，例如每次返回 `{ theme: currentTheme }`；如果确实需要对象快照，先在 store 内部缓存对象，只在底层数据变化时替换引用。

**检查**：看到组件用 `useEffect` 订阅外部 store 并立刻 `setState(store.get())` 时，追问三件事：首次 render 是否已经拿到快照、并发渲染期间快照是否一致、SSR hydration 的默认值是否一致。
