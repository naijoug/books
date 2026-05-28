# `asyncio.gather` 适合批量等待同类 I/O

**问题**：如何同时等待一组网络请求、数据库查询或文件 I/O？

**要点**：

- `asyncio.gather()` 会并发等待多个 awaitable，并按传入顺序返回结果。
- 它提升的是等待效率，不会让 CPU 计算自动变快。
- 批量 I/O 仍要配合超时、并发上限和错误处理。

**示例**：

```python
import asyncio
from typing import List, Tuple, Union

Event = Tuple[str, str]


async def fetch_page(name: str, events: List[Event], *, fail: bool = False) -> str:
    events.append(("start", name))
    await asyncio.sleep(0)  # 模拟网络、数据库或文件 I/O 的等待点
    events.append(("finish", name))
    if fail:
        raise RuntimeError(f"{name} failed")
    return f"page:{name}"


async def fetch_with_limit(
    name: str,
    semaphore: asyncio.Semaphore,
    events: List[Event],
    active: List[int],
) -> str:
    async with semaphore:
        active.append(active[-1] + 1)
        assert active[-1] <= 2
        result = await fetch_page(name, events)
        active.append(active[-1] - 1)
        return result


async def main() -> None:
    events: List[Event] = []

    pages = await asyncio.gather(
        fetch_page("slow", events),
        fetch_page("fast", events),
    )

    assert pages == ["page:slow", "page:fast"]  # 返回值按传入顺序，不按完成顺序
    assert events[:2] == [("start", "slow"), ("start", "fast")]
    assert sorted(events[2:]) == [("finish", "fast"), ("finish", "slow")]

    failures: Tuple[Union[str, BaseException], Union[str, BaseException]] = await asyncio.gather(
        fetch_page("ok", []),
        fetch_page("bad", [], fail=True),
        return_exceptions=True,
    )
    assert failures[0] == "page:ok"
    assert isinstance(failures[1], RuntimeError)

    limited_events: List[Event] = []
    active = [0]
    semaphore = asyncio.Semaphore(2)
    limited_pages = await asyncio.gather(
        *(fetch_with_limit(str(i), semaphore, limited_events, active) for i in range(5))
    )
    assert limited_pages == ["page:0", "page:1", "page:2", "page:3", "page:4"]
    assert active[-1] == 0


asyncio.run(main())
```

把代码保存为 `asyncio-gather-batch-io.py` 后运行：

```bash
python3 asyncio-gather-batch-io.py
```

正常情况下没有输出，退出码为 0；如果把 `pages` 的期望顺序改成完成顺序，断言会失败。

**坑**：无限制地把几千个请求一次性丢进 `gather()`，可能压垮自己或对方服务；需要搭配 `Semaphore` 或连接池限制。默认情况下，一个任务抛错会让 `gather()` 向外抛出异常；如果希望收集每个任务的成功/失败结果，需要显式设置 `return_exceptions=True` 并逐个处理。

**检查**：任务是否主要在等外部系统？如果是，`gather()` 有价值；如果主要在做本地计算，优先考虑进程池或算法优化。检查点包括：返回顺序是否依赖输入顺序、是否限制了并发、单个失败是否会影响整批结果。
