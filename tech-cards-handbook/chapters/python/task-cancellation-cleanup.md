# 取消任务时要让清理逻辑运行

**问题**：异步任务超时或取消后，如何避免连接、锁、临时文件泄漏？

**要点**：

- `CancelledError` 会在 `await` 点抛出。
- 清理逻辑放在 `finally` 中。
- 不要无条件吞掉 `CancelledError`，否则上层以为任务还正常完成。

**示例**：

```python
import asyncio

async def worker() -> None:
    resource = "connection"
    try:
        while True:
            await asyncio.sleep(1)
            print("working")
    finally:
        print(f"closing {resource}")

async def main() -> None:
    task = asyncio.create_task(worker())
    await asyncio.sleep(2.5)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("worker cancelled")

asyncio.run(main())
```

**坑**：`except Exception` 捕获不到 `CancelledError` 的语义边界在不同版本里有变化，不要依赖宽泛捕获处理取消。

**检查**：给长任务写一个取消测试，确认取消后资源释放日志或状态确实发生。
