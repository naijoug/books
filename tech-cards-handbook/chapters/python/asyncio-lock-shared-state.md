# `asyncio.Lock` 保护共享状态

**问题**：单线程事件循环里为什么还会有竞态条件？

**要点**：

- 只要在“读-改-写”中间出现 `await`，其他任务就可能插入。
- `Lock` 保护的是临界区，不是整个函数。
- 临界区越短越好。

**示例**：

```python
import asyncio

class SharedCounter:
    def __init__(self) -> None:
        self.value = 0
        self.lock = asyncio.Lock()

    async def increment(self) -> None:
        async with self.lock:
            current = self.value
            await asyncio.sleep(0.01)
            self.value = current + 1

async def main() -> None:
    counter = SharedCounter()
    await asyncio.gather(*(counter.increment() for _ in range(50)))
    print(counter.value)

asyncio.run(main())
```

**坑**：不要在持锁期间做慢 I/O，除非共享状态必须覆盖这段 I/O。

**检查**：临界区内是否只包含必须串行的状态读写？
