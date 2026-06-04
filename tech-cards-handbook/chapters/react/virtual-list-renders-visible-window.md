# 虚拟列表只渲染可见窗口，不渲染整页数据

**问题**：列表有几千行，搜索、滚动或切换筛选时很卡。应该给每一行都加 `memo`，还是减少同时渲染的 DOM 数量？

**要点**：

- 长列表的核心成本通常不是某一行组件太复杂，而是一次提交里渲染了太多行。
- 虚拟列表只渲染当前视口附近的窗口，用顶部/底部占位高度保持滚动条尺寸。
- `memo` 只能减少不必要的重复渲染，不能降低首次渲染 5000 个节点的 DOM 成本。
- 固定行高最容易实现；可变行高需要测量缓存和滚动锚点，先不要在产品里手写复杂版本。
- 给窗口额外保留少量 overscan，避免滚动时出现空白。

**示例**：

```tsx
import { useMemo, useState } from "react";

type Message = {
  id: string;
  author: string;
  text: string;
};

const ROW_HEIGHT = 48;
const VIEWPORT_HEIGHT = 320;
const OVERSCAN = 4;

function MessageRow({ message }: { key?: string; message: Message }) {
  return (
    <div style={{ height: ROW_HEIGHT, borderBottom: "1px solid #eee" }}>
      <strong>{message.author}</strong>: {message.text}
    </div>
  );
}

export function VirtualMessageList({ messages }: { messages: Message[] }) {
  const [scrollTop, setScrollTop] = useState(0);

  const windowState = useMemo(() => {
    const firstVisible = Math.floor(scrollTop / ROW_HEIGHT);
    const visibleCount = Math.ceil(VIEWPORT_HEIGHT / ROW_HEIGHT);
    const start = Math.max(0, firstVisible - OVERSCAN);
    const end = Math.min(messages.length, firstVisible + visibleCount + OVERSCAN);

    return {
      start,
      end,
      topPadding: start * ROW_HEIGHT,
      bottomPadding: (messages.length - end) * ROW_HEIGHT,
      visibleMessages: messages.slice(start, end),
    };
  }, [messages, scrollTop]);

  return (
    <div
      style={{ height: VIEWPORT_HEIGHT, overflow: "auto" }}
      onScroll={(event: { currentTarget: { scrollTop: number } }) => {
        setScrollTop(event.currentTarget.scrollTop);
      }}
    >
      <div style={{ height: windowState.topPadding }} />
      {windowState.visibleMessages.map((message) => (
        <MessageRow key={message.id} message={message} />
      ))}
      <div style={{ height: windowState.bottomPadding }} />
    </div>
  );
}
```

上面即使 `messages` 有 10000 条，真实渲染的行数也接近 `VIEWPORT_HEIGHT / ROW_HEIGHT + OVERSCAN * 2`。滚动条仍然能反映整份数据长度，因为不可见区域由 padding 占位。

**坑**：

- 先给每一行加 `memo`，但仍然一次渲染全量数据；这通常治标不治本。
- 行高并不固定，却按固定高度计算窗口，会导致滚动位置和内容错位。
- overscan 太小会快速滚动时闪白，太大又会把渲染成本加回来。
- 用数组索引当 `key`，筛选或插入数据后会复用错行状态。
- 忘记给容器固定高度和 `overflow: auto`，导致窗口计算失去边界。

**检查**：用 Profiler 对比同一份 5000 行数据的首次打开和滚动交互：提交中实际渲染的行数是否稳定在几十行？滚动条高度、键盘/鼠标滚动和筛选后的第一屏是否都正确？
