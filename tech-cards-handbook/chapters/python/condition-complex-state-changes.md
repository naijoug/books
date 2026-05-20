# `Condition` 用于等待复杂状态变化

**问题**：既要互斥访问共享缓冲区，又要等“有空间”或“有数据”，怎么写？

**要点**：

- `Condition` 组合了锁和等待通知。
- 等待条件必须放在 `while` 循环里重复检查。
- 状态改变后用 `notify()` 或 `notify_all()` 唤醒等待者。

**示例**：

```python
import asyncio

class SharedBuffer:
    def __init__(self, size: int) -> None:
        self.items: list[int] = []
        self.size = size
        self.condition = asyncio.Condition()

    async def put(self, item: int) -> None:
        async with self.condition:
            while len(self.items) >= self.size:
                await self.condition.wait()
            self.items.append(item)
            self.condition.notify_all()

    async def get(self) -> int:
        async with self.condition:
            while not self.items:
                await self.condition.wait()
            item = self.items.pop(0)
            self.condition.notify_all()
            return item
```

**坑**：不要用 `if` 替代 `while`。被唤醒不代表条件一定仍然成立。

**检查**：每个 `wait()` 前后是否都围绕真实业务条件判断？
