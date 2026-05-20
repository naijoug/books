# `asyncio` 不是让代码更快，而是减少等待浪费

**问题**：什么时候应该用异步，而不是多线程或普通同步代码？

**要点**：

- 适合 I/O 密集任务：HTTP 请求、数据库查询、文件/网络等待。
- 不适合 CPU 密集任务：图片处理、压缩、复杂计算。
- 异步函数只有被 `await`、`asyncio.run()` 或任务调度后才会执行。

**示例**：

```python
import asyncio
import httpx

async def fetch(url: str) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

async def main() -> None:
    urls = ["https://example.com", "https://www.python.org"]
    pages = await asyncio.gather(*(fetch(url) for url in urls))
    print([len(page) for page in pages])

asyncio.run(main())
```

**坑**：在 `async def` 里调用阻塞函数，例如 `time.sleep()` 或同步 HTTP 客户端，会卡住整个事件循环。

**检查**：如果任务大部分时间在等外部系统，异步通常有价值；如果任务一直占满 CPU，考虑进程池或专门的计算库。
