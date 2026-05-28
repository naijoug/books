# 取消任务时要让清理逻辑运行

**问题**：异步任务超时或取消后，如何避免连接、锁、临时文件泄漏？

**要点**：

- `CancelledError` 会在 `await` 点抛出。
- 清理逻辑放在 `finally` 中。
- 不要无条件吞掉 `CancelledError`，否则上层以为任务还正常完成。

**示例**：

```python
import asyncio
from typing import List

async def worker(events: List[str]) -> None:
    resource = "connection"
    events.append(f"open:{resource}")
    try:
        while True:
            events.append("tick")
            await asyncio.sleep(0)
    finally:
        # 取消会在 await 点抛出，但 finally 仍然会运行。
        events.append(f"close:{resource}")

async def stubborn_worker(events: List[str]) -> str:
    try:
        events.append("started")
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        events.append("cancel-swallowed")
        return "looks-ok"
    return "done"

async def main() -> None:
    events: List[str] = []
    task = asyncio.create_task(worker(events))
    await asyncio.sleep(0)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        events.append("cancel-propagated")

    assert task.cancelled()
    assert events[0] == "open:connection"
    assert "tick" in events
    assert events[-2:] == ["close:connection", "cancel-propagated"]

    swallowed: List[str] = []
    bad_task = asyncio.create_task(stubborn_worker(swallowed))
    await asyncio.sleep(0)
    bad_task.cancel()
    result = await bad_task

    assert result == "looks-ok"
    assert not bad_task.cancelled()
    assert swallowed == ["started", "cancel-swallowed"]

asyncio.run(main())
```

保存为 `task-cancellation-cleanup.py` 后执行 `python3 task-cancellation-cleanup.py`，应无输出、无异常。第一组断言确认 `cancel()` 后 `finally` 一定关闭资源且 `CancelledError` 继续向上层传播；第二组断言故意吞掉取消信号，说明上层会把任务误判为正常完成。

**坑**：不要用宽泛捕获顺手吞掉取消信号；如果必须在 `except asyncio.CancelledError` 中记录日志或更新状态，处理完应再次 `raise`，否则调用方无法通过 `await task` 或 `task.cancelled()` 观察到真正的取消。

**检查**：给长任务写一个取消测试，确认取消后资源释放状态发生，并确认上层仍能观察到 `CancelledError`。
