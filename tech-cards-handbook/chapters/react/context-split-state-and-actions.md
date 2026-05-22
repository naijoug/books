# Context 拆分状态和动作，避免全树重渲染

## 问题

把一个很大的对象直接塞进 Context Provider 后，只要其中任意字段变化，所有读取这个 Context 的组件都会重新渲染。主题、用户、权限、表单草稿、操作函数混在一个 `value` 里时，页面越大，重渲染越难定位。

## 要点

- Context 适合传递“跨层级共享”的值，不适合承载所有局部状态。
- Provider 的 `value` 身份变化会通知所有消费者；每次 render 临时创建 `{ state, actions }` 会放大影响范围。
- 经常一起变化、一起读取的值放在同一个 Context；变化频率不同或读写用途不同的值拆成多个 Context。
- 动作函数可以单独放进 Actions Context，并用 `useMemo`/`useCallback` 稳定 Provider value。
- 高频更新的输入态、鼠标位置、列表滚动位置优先靠近使用处；不要因为“方便传递”就提升到全局 Context。

## 示例

```tsx
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

type Theme = "light" | "dark";
type ThemeActions = {
  toggleTheme: () => void;
};

const ThemeStateContext = createContext<Theme | null>(null);
const ThemeActionsContext = createContext<ThemeActions | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");

  const toggleTheme = useCallback(() => {
    setTheme((current) => (current === "light" ? "dark" : "light"));
  }, []);

  const actions = useMemo(() => ({ toggleTheme }), [toggleTheme]);

  return (
    <ThemeStateContext.Provider value={theme}>
      <ThemeActionsContext.Provider value={actions}>
        {children}
      </ThemeActionsContext.Provider>
    </ThemeStateContext.Provider>
  );
}

export function useTheme() {
  const theme = useContext(ThemeStateContext);
  if (theme === null) {
    throw new Error("useTheme must be used inside ThemeProvider");
  }
  return theme;
}

export function useThemeActions() {
  const actions = useContext(ThemeActionsContext);
  if (actions === null) {
    throw new Error("useThemeActions must be used inside ThemeProvider");
  }
  return actions;
}
```

只需要触发操作的按钮可以读取 `useThemeActions()`，不必订阅 `theme` 状态；只展示主题的组件读取 `useTheme()`，不关心动作对象。这样读写职责更清楚，重渲染范围也更容易检查。

## 坑

- 把 `value={{ theme, toggleTheme }}` 直接写在 JSX 里：对象每次都是新身份，即使 `theme` 没变，也会通知消费者。
- 把用户信息、权限、主题、弹窗状态、表单输入全部塞进一个 Context：任何字段变化都会影响所有消费者。
- 误以为拆 Context 一定能解决所有性能问题：如果一个组件同时读取多个变化频繁的 Context，它仍会随这些值变化而渲染。
- 为了少写 Provider 过度全局化状态：Context 不是状态管理银弹，局部状态仍应留在局部。

## 检查

- 这个值是否真的需要跨很多层传递？如果只在一小段子树使用，优先组件组合或局部状态。
- Provider 的 `value` 是否是稳定身份？对象、数组和函数是否通过 `useMemo`/`useCallback` 控制了依赖？
- 是否存在“只需要 action 的组件却订阅了 state”的情况？可以拆成 State Context 和 Actions Context。
- 用 React DevTools Profiler 触发一次状态变化，确认无关组件没有因为同一个大 Context 被动重渲染。
