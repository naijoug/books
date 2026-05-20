# 超时是异步系统的基本边界

**问题**：如何避免一个慢请求让整个流程无限等待？

**要点**：

- `asyncio.wait_for` 可以给单个 awaitable 加超时。
- 超时后底层任务会被取消。
- 取消后仍要确保资源清理逻辑运行。

**示例**：

```python
import asyncio

async def slow_operation() -> str:
    await asyncio.sleep(5)
    return "done"

async def main() -> None:
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=1)
        print(result)
    except asyncio.TimeoutError:
        print("operation timed out")

asyncio.run(main())
```

**坑**：只在最外层加一个巨大超时不够。数据库、HTTP、队列等待通常都需要各自的边界。

**检查**：所有外部 I/O 是否都有明确超时？
