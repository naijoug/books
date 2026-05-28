# `asyncio` 不是让代码更快，而是减少等待浪费

**问题**：什么时候应该用异步，而不是多线程或普通同步代码？

**要点**：

- 适合 I/O 密集任务：HTTP 请求、数据库查询、文件/网络等待。
- 不适合 CPU 密集任务：图片处理、压缩、复杂计算。
- 异步函数只有被 `await`、`asyncio.run()` 或任务调度后才会执行。

**示例**：

```python
import asyncio
from typing import List

async def fake_fetch(name: str, events: List[str]) -> str:
    events.append(f"start:{name}")
    await asyncio.sleep(0)  # 模拟一次网络/数据库等待，把控制权还给事件循环
    events.append(f"done:{name}")
    return f"page:{name}"

async def main() -> None:
    events: List[str] = []

    coroutine = fake_fetch("not-scheduled", events)
    assert events == []  # 只创建协程对象时，函数体还没有执行
    coroutine.close()

    pages = await asyncio.gather(
        fake_fetch("docs", events),
        fake_fetch("blog", events),
    )

    assert pages == ["page:docs", "page:blog"]  # gather 按传入顺序返回结果
    assert events[:2] == ["start:docs", "start:blog"]  # 两个任务都先启动，再一起等待 I/O
    assert sorted(events[2:]) == ["done:blog", "done:docs"]

asyncio.run(main())
```

把代码保存为 `asyncio-reduces-waiting.py` 后运行 `python3 asyncio-reduces-waiting.py`；无输出且退出码为 0，说明协程调度、结果顺序和“未 await 不执行”的断言都通过。

**坑**：在 `async def` 里调用阻塞函数，例如 `time.sleep()` 或同步 HTTP 客户端，会卡住整个事件循环；如果只是把 CPU 密集计算包进 `async def`，也不会自动变快。

**检查**：如果任务大部分时间在等外部系统，异步通常有价值；如果任务一直占满 CPU，考虑进程池或专门的计算库。先用一个本地可运行断言证明“等待被交错”，再把 `fake_fetch()` 替换成真实 HTTP/数据库调用。
