# `TaskGroup` 让一组任务同生共死

**问题**：多个子任务中一个失败时，如何避免其他任务继续乱跑？

**要点**：

- Python 3.11+ 提供 `asyncio.TaskGroup`。
- 任务组内有任务失败时，其他任务会被取消。
- 离开 `async with` 时，任务组内任务都已结束。

**示例**：

```python
import asyncio

async def job(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return name

async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        a = tg.create_task(job("a", 0.3))
        b = tg.create_task(job("b", 0.1))

    print(a.result(), b.result())

asyncio.run(main())
```

**坑**：`create_task` 裸奔时，任务生命周期容易失控；异常可能只在日志里出现。

**检查**：这组任务是否属于同一个上层操作？是的话优先用 TaskGroup 管理生命周期。
