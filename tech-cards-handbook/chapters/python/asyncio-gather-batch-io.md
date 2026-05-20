# `asyncio.gather` 适合批量等待同类 I/O

**问题**：如何同时等待一组网络请求、数据库查询或文件 I/O？

**要点**：

- `asyncio.gather()` 会并发等待多个 awaitable，并按传入顺序返回结果。
- 它提升的是等待效率，不会让 CPU 计算自动变快。
- 批量 I/O 仍要配合超时、并发上限和错误处理。

**示例**：

```python
import asyncio
import aiohttp

async def download(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()

async def main(urls: list[str]) -> None:
    async with aiohttp.ClientSession() as session:
        pages = await asyncio.gather(*(download(session, url) for url in urls))
    print([len(page) for page in pages])
```

**坑**：无限制地把几千个请求一次性丢进 `gather()`，可能压垮自己或对方服务；需要搭配 `Semaphore` 或连接池限制。

**检查**：任务是否主要在等外部系统？如果是，`gather()` 有价值；如果主要在做本地计算，优先考虑进程池或算法优化。
