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

    async def poke(self) -> None:
        """模拟一次没有改变状态的唤醒。"""
        async with self.condition:
            self.condition.notify_all()

async def main() -> None:
    buffer = SharedBuffer(size=1)

    blocked_get = asyncio.create_task(buffer.get())
    await asyncio.sleep(0)
    assert not blocked_get.done()

    await buffer.poke()
    await asyncio.sleep(0)
    assert not blocked_get.done()  # while 会在假唤醒后继续等待

    await buffer.put(1)
    assert await blocked_get == 1
    assert buffer.items == []

    await buffer.put(2)
    blocked_put = asyncio.create_task(buffer.put(3))
    await asyncio.sleep(0)
    assert not blocked_put.done()
    assert buffer.items == [2]

    assert await buffer.get() == 2
    await blocked_put
    assert buffer.items == [3]

asyncio.run(main())
```

把代码保存为 `condition-complex-state-changes.py` 后运行 `python3 condition-complex-state-changes.py`。脚本没有输出且退出码为 0，说明空缓冲区会阻塞消费者、满缓冲区会阻塞生产者，`notify_all()` 只负责唤醒，真正的业务条件仍由 `while` 重新检查。

**坑**：不要用 `if` 替代 `while`。被唤醒不代表条件一定仍然成立；可能是假唤醒，也可能是其他任务先抢到锁并改变了缓冲区状态。

**检查**：每个 `wait()` 前后是否都围绕真实业务条件判断？满/空两种边界是否都有可运行断言？
