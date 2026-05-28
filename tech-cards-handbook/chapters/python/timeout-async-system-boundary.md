# 超时是异步系统的基本边界

**问题**：如何避免一个慢请求让整个流程无限等待？

**要点**：

- `asyncio.wait_for` 可以给单个 awaitable 加超时。
- 超时后底层任务会被取消。
- 取消后仍要确保资源清理逻辑运行。

**示例**：

```python
import asyncio
from typing import List

async def slow_operation(events: List[str]) -> str:
    events.append("open")
    try:
        await asyncio.sleep(10)
        events.append("done")
        return "done"
    finally:
        events.append("cleanup")

async def fast_operation(events: List[str]) -> str:
    events.append("fast-start")
    await asyncio.sleep(0)
    events.append("fast-done")
    return "ok"

async def main() -> None:
    timed_out_events: List[str] = []
    try:
        await asyncio.wait_for(slow_operation(timed_out_events), timeout=0.01)
    except asyncio.TimeoutError:
        timed_out_events.append("timeout")

    assert timed_out_events == ["open", "cleanup", "timeout"]

    fast_events: List[str] = []
    result = await asyncio.wait_for(fast_operation(fast_events), timeout=1)
    assert result == "ok"
    assert fast_events == ["fast-start", "fast-done"]

    cancelled_events: List[str] = []
    task = asyncio.create_task(slow_operation(cancelled_events))
    await asyncio.sleep(0)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        cancelled_events.append("cancelled")

    assert cancelled_events == ["open", "cleanup", "cancelled"]
    assert task.cancelled()

asyncio.run(main())
```

把代码保存为 `timeout-async-system-boundary.py` 后运行 `python3 timeout-async-system-boundary.py`，应无输出且退出码为 0。这个脚本同时检查三件事：慢操作超时后会执行 `finally` 清理并向外表现为 `TimeoutError`，快操作在边界内正常返回，手动取消任务时同样会触发清理并保留取消状态。

**坑**：只在最外层加一个巨大超时不够。数据库、HTTP、队列等待通常都需要各自的边界；被 `wait_for` 超时的底层任务会收到取消信号，不要在内部吞掉 `CancelledError`，否则上层会误判边界已经收敛。

**检查**：所有外部 I/O 是否都有明确超时？超时或取消后，连接、锁、临时文件等资源是否一定在 `finally` 中释放？
