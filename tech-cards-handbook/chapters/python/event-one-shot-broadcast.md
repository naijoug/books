# `Event` 适合一次性广播通知

**问题**：多个任务都要等待“配置加载完成”或“服务准备好”，怎么通知？

**要点**：

- `Event.wait()` 等待事件发生。
- `Event.set()` 会唤醒所有已经等待的任务。
- 事件一旦 set，后续 `wait()` 会立即通过，除非手动 `clear()`。
- `Event` 只表达“发生过”，不携带数据，也不记录发生次数。

**示例**：

```python
import asyncio
from typing import List

async def waiter(event: asyncio.Event, name: str, events: List[str]) -> str:
    events.append(f"{name}:waiting")
    await event.wait()
    events.append(f"{name}:started")
    return name

async def main() -> None:
    event = asyncio.Event()
    events: List[str] = []

    tasks = [
        asyncio.create_task(waiter(event, f"worker-{i}", events))
        for i in range(3)
    ]

    # 先把控制权交给等待者；此时事件尚未 set，它们只会停在 wait()。
    await asyncio.sleep(0)
    assert events == [
        "worker-0:waiting",
        "worker-1:waiting",
        "worker-2:waiting",
    ]
    assert all(not task.done() for task in tasks)

    event.set()
    assert await asyncio.gather(*tasks) == ["worker-0", "worker-1", "worker-2"]
    assert events == [
        "worker-0:waiting",
        "worker-1:waiting",
        "worker-2:waiting",
        "worker-0:started",
        "worker-1:started",
        "worker-2:started",
    ]

    # set 之后才来的等待者会立即通过：Event 是“门已经打开”，不是“发一次消息”。
    late_events: List[str] = []
    assert await waiter(event, "late-worker", late_events) == "late-worker"
    assert late_events == ["late-worker:waiting", "late-worker:started"]

    event.clear()
    blocked = asyncio.create_task(waiter(event, "blocked-worker", events))
    await asyncio.sleep(0)
    assert not blocked.done()
    event.set()
    assert await blocked == "blocked-worker"

asyncio.run(main())
```

把代码保存为 `event-one-shot-broadcast.py` 后运行 `python3 event-one-shot-broadcast.py`；无输出且退出码为 0，说明已等待任务会被一次性唤醒、后续等待者会立即通过、`clear()` 后会重新阻塞。

**坑**：`Event` 不携带数据，也不会像计数器一样记录 `set()` 发生了几次。需要传递任务数据时用 `Queue`；需要“每次通知都不能丢”时不要只靠 `Event`。

**检查**：你需要的是“通知某个状态已经发生”，还是“传递一批数据/每次事件都要消费”？前者用 `Event`，后者优先用 `Queue` 或显式状态加锁。
