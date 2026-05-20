# `Event` 适合一次性广播通知

**问题**：多个任务都要等待“配置加载完成”或“服务准备好”，怎么通知？

**要点**：

- `Event.wait()` 等待事件发生。
- `Event.set()` 会唤醒所有等待者。
- 事件一旦 set，后续 `wait()` 会立即通过，除非手动 `clear()`。

**示例**：

```python
import asyncio

async def waiter(event: asyncio.Event, name: str) -> None:
    print(f"{name} waiting")
    await event.wait()
    print(f"{name} started")

async def main() -> None:
    event = asyncio.Event()
    tasks = [asyncio.create_task(waiter(event, f"worker-{i}")) for i in range(3)]
    await asyncio.sleep(1)
    event.set()
    await asyncio.gather(*tasks)

asyncio.run(main())
```

**坑**：`Event` 不携带数据。需要传递任务数据时用 `Queue`。

**检查**：你需要的是“通知发生了”，还是“传递一批数据”？前者用 Event，后者用 Queue。
