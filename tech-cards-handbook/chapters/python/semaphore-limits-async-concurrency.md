# `Semaphore` 限制同时运行的异步任务数

**问题**：有 1000 个 URL 要请求，为什么不能直接 `gather` 全部任务？

**要点**：

- `asyncio.gather` 会并发调度所有传入协程。
- 外部 API、数据库、文件句柄都有容量上限。
- `Semaphore` 用于限制临界区内同时运行的任务数。

**示例**：

```python
import asyncio

async def fetch_url(url: str, semaphore: asyncio.Semaphore) -> str:
    async with semaphore:
        print(f"fetching {url}")
        await asyncio.sleep(1)
        return f"result from {url}"

async def main() -> None:
    semaphore = asyncio.Semaphore(3)
    urls = [f"https://example.com/{i}" for i in range(10)]
    results = await asyncio.gather(
        *(fetch_url(url, semaphore) for url in urls)
    )
    print(len(results))

asyncio.run(main())
```

**坑**：并发数不是越大越快。超过下游限流或连接池上限后，只会增加超时、重试和排队。

**检查**：并发上限是否来自下游容量，例如 API QPS、数据库连接池、文件描述符限制？
