# `Semaphore` 限制同时运行的异步任务数

**问题**：有 1000 个 URL 要请求，为什么不能直接 `gather` 全部任务？

**要点**：

- `asyncio.gather` 会并发调度所有传入协程。
- 外部 API、数据库、文件句柄都有容量上限。
- `Semaphore` 用于限制临界区内同时运行的任务数。
- 并发上限要包住真正消耗下游容量的那段代码，而不是包住任务创建本身。

**示例**：

```python
import asyncio
from typing import List

async def fetch_url(
    url: str,
    semaphore: asyncio.Semaphore,
    events: List[str],
    active_counts: List[int],
) -> str:
    async with semaphore:
        running_before_start = len(
            [event for event in events if event.startswith("start:")]
        ) - len([event for event in events if event.startswith("done:")])
        active_counts.append(running_before_start + 1)
        events.append(f"start:{url}")
        await asyncio.sleep(0)
        events.append(f"done:{url}")
        return f"result from {url}"

async def main() -> None:
    semaphore = asyncio.Semaphore(3)
    urls = [f"url-{i}" for i in range(10)]
    events: List[str] = []
    active_counts: List[int] = []

    results = await asyncio.gather(
        *(fetch_url(url, semaphore, events, active_counts) for url in urls)
    )

    assert results == [f"result from url-{i}" for i in range(10)]
    assert len([event for event in events if event.startswith("start:")]) == 10
    assert len([event for event in events if event.startswith("done:")]) == 10
    assert max(active_counts) <= 3

asyncio.run(main())
```

把代码保存为 `semaphore-limits-async-concurrency.py` 后运行：

```bash
python3 semaphore-limits-async-concurrency.py
```

没有输出且退出码为 0，说明所有断言通过；如果把 `Semaphore(3)` 暂时改成 `Semaphore(10)`，`max(active_counts) <= 3` 会失败，用来确认测试真的覆盖了并发上限。

**坑**：并发数不是越大越快。超过下游限流或连接池上限后，只会增加超时、重试和排队。也不要把 `async with semaphore` 放在太外层，否则会把不需要限流的准备工作也串进等待队列。

**检查**：并发上限是否来自下游容量，例如 API QPS、数据库连接池、文件描述符限制？能否用断言或指标证明实际并发数没有超过这个上限？
