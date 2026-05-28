# `Queue` 让生产者和消费者解耦

**问题**：生产速度和消费速度不一致时，如何避免互相阻塞或内存暴涨？

**要点**：

- `asyncio.Queue(maxsize=N)` 可以提供背压。
- 生产者 `put`，消费者 `get`。
- 每个 `get` 后要调用 `task_done()`，配合 `queue.join()` 等待清空。

**示例**：

```python
import asyncio
from typing import List, Optional

SENTINEL = None

async def producer(
    queue: "asyncio.Queue[Optional[int]]",
    items: List[int],
    consumer_count: int,
) -> None:
    for item in items:
        await queue.put(item)
        assert queue.qsize() <= queue.maxsize

    # 有几个消费者，就放几个结束信号；否则某些消费者会永远等在 get()。
    for _ in range(consumer_count):
        await queue.put(SENTINEL)

async def consumer(
    name: str,
    queue: "asyncio.Queue[Optional[int]]",
    consumed: List[str],
) -> None:
    while True:
        item = await queue.get()
        try:
            if item is SENTINEL:
                consumed.append(f"{name}:stop")
                return
            consumed.append(f"{name}:{item}")
            await asyncio.sleep(0)
        finally:
            queue.task_done()

async def main() -> None:
    items = list(range(6))
    consumer_count = 2
    queue: "asyncio.Queue[Optional[int]]" = asyncio.Queue(maxsize=2)
    consumed: List[str] = []

    consumers = [
        asyncio.create_task(consumer(f"c{index}", queue, consumed))
        for index in range(consumer_count)
    ]
    await producer(queue, items, consumer_count)
    await queue.join()
    await asyncio.gather(*consumers)

    consumed_items = sorted(
        int(entry.split(":", 1)[1])
        for entry in consumed
        if not entry.endswith(":stop")
    )
    stop_events = [entry for entry in consumed if entry.endswith(":stop")]

    assert consumed_items == items
    assert len(stop_events) == consumer_count
    assert queue.empty()

asyncio.run(main())
```

把示例保存为 `queue-decouples-producers-consumers.py` 后运行：

```bash
python3 queue-decouples-producers-consumers.py
```

命令应无输出、无异常；如果把结束信号数量改成 `1`，其中一个消费者会卡在 `queue.get()`，说明多消费者场景必须显式设计停止协议。

**坑**：多个消费者时，结束信号也要发送多个，或者使用取消机制统一停止消费者；`queue.join()` 依赖每次 `get()` 都匹配一次 `task_done()`，漏掉会永久等待。

**检查**：队列是否设置了 `maxsize`？没有上限的队列可能把内存当缓冲区烧掉；是否有测试证明所有任务都被消费、消费者能退出、队列最终为空？
