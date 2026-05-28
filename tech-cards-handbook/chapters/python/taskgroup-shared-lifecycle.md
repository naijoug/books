# `TaskGroup` 让一组任务同生共死

**问题**：多个子任务中一个失败时，如何避免其他任务继续乱跑？

**要点**：

- Python 3.11+ 提供 `asyncio.TaskGroup`。
- 任务组内有任务失败时，其他仍在运行的任务会被取消。
- 离开 `async with` 时，任务组内任务都已结束；成功任务可安全读取 `result()`。
- 多个异常会被包装成 `ExceptionGroup`，需要用 `except*` 按异常类型处理。

**示例**：

```python
import asyncio

async def job(name: str, delay: float, events: list[str]) -> str:
    events.append(f"{name}:start")
    try:
        await asyncio.sleep(delay)
        events.append(f"{name}:done")
        return name
    except asyncio.CancelledError:
        events.append(f"{name}:cancelled")
        raise

async def fail_fast(events: list[str]) -> None:
    events.append("fail:start")
    await asyncio.sleep(0.01)
    events.append("fail:raise")
    raise RuntimeError("boom")

async def successful_group() -> tuple[str, str, list[str]]:
    events: list[str] = []

    async with asyncio.TaskGroup() as tg:
        a = tg.create_task(job("a", 0.02, events))
        b = tg.create_task(job("b", 0.01, events))

    assert a.done() and b.done()
    return a.result(), b.result(), events

async def failing_group() -> list[str]:
    events: list[str] = []
    captured: tuple[BaseException, ...] = ()

    try:
        async with asyncio.TaskGroup() as tg:
            slow = tg.create_task(job("slow", 10, events))
            boom = tg.create_task(fail_fast(events))
    except* RuntimeError as group:
        captured = group.exceptions

    assert len(captured) == 1
    assert str(captured[0]) == "boom"
    assert slow.cancelled()
    assert boom.done()
    assert "slow:cancelled" in events
    return events

async def main() -> None:
    first, second, success_events = await successful_group()
    assert (first, second) == ("a", "b")
    assert success_events == ["a:start", "b:start", "b:done", "a:done"]

    failure_events = await failing_group()
    assert failure_events == ["slow:start", "fail:start", "fail:raise", "slow:cancelled"]

asyncio.run(main())
```

把代码保存为 `taskgroup-shared-lifecycle.py` 后执行 `python3.11 taskgroup-shared-lifecycle.py`；无输出且退出码为 0，说明成功场景的结果读取、失败场景的异常聚合和兄弟任务取消都符合预期。

**坑**：`create_task` 裸奔时，任务生命周期容易失控；异常可能只在日志里出现。`TaskGroup` 会帮你收拢生命周期，但不会替你吞异常，外层仍要处理 `ExceptionGroup`。

**检查**：这组任务是否属于同一个上层操作？是的话优先用 TaskGroup 管理生命周期，并为“一个失败时其他任务被取消”的分支写断言。
