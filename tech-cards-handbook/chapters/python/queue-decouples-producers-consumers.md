# `Queue` 让生产者和消费者解耦

**问题**：生产速度和消费速度不一致时，如何避免互相阻塞或内存暴涨？

**要点**：

- `asyncio.Queue(maxsize=N)` 可以提供背压。
- 生产者 `put`，消费者 `get`。
- 每个 `get` 后要调用 `task_done()`，配合 `queue.join()` 等待清空。

**示例**：

```python
import asyncio

async def producer(queue: asyncio.Queue[int | None]) -> None:
    for item in range(10):
        await queue.put(item)
    await queue.put(None)

async def consumer(queue: asyncio.Queue[int | None]) -> None:
    while True:
        item = await queue.get()
        try:
            if item is None:
                return
            print(f"consume {item}")
            await asyncio.sleep(0.2)
        finally:
            queue.task_done()

async def main() -> None:
    queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=5)
    await asyncio.gather(producer(queue), consumer(queue))
    await queue.join()

asyncio.run(main())
```

**坑**：多个消费者时，结束信号也要发送多个，或者使用取消机制统一停止消费者。

**检查**：队列是否设置了 `maxsize`？没有上限的队列可能把内存当缓冲区烧掉。
