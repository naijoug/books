# `asyncio.run()` 是异步程序的同步入口

**问题**：什么时候用 `asyncio.run()`，什么时候只写 `await`？

**要点**：

- `async def` 只是在定义协程函数，调用后得到协程对象，并不会立刻执行。
- 顶层脚本通常用 `asyncio.run(main())` 启动事件循环。
- 已经在事件循环内部时，不要再调用 `asyncio.run()`，应该直接 `await`。

**示例**：

```python
import asyncio

events: list[str] = []

async def make_coffee() -> str:
    events.append("coffee:start")
    await asyncio.sleep(0)
    events.append("coffee:end")
    return "coffee"

async def make_toast() -> str:
    events.append("toast:start")
    await asyncio.sleep(0)
    events.append("toast:end")
    return "toast"

async def cannot_run_inside_loop() -> None:
    coro = make_coffee()
    try:
        asyncio.run(coro)
    except RuntimeError as exc:
        assert "asyncio.run() cannot be called" in str(exc)
        coro.close()  # 避免未 await 的协程警告。
    else:
        raise AssertionError("asyncio.run() should fail inside a running loop")

async def main() -> tuple[str, str]:
    coroutine = make_coffee()
    assert events == []  # 调用 async 函数只创建协程，还没有执行函数体。
    coroutine.close()

    coffee, toast = await asyncio.gather(make_coffee(), make_toast())
    assert (coffee, toast) == ("coffee", "toast")
    assert events == [
        "coffee:start",
        "toast:start",
        "coffee:end",
        "toast:end",
    ]

    await cannot_run_inside_loop()
    return coffee, toast

if __name__ == "__main__":
    assert asyncio.run(main()) == ("coffee", "toast")
```

把这段保存为 `asyncio-run-sync-entrypoint.py` 后执行 `python3 asyncio-run-sync-entrypoint.py`。脚本无输出且退出码为 0，说明 `asyncio.run()` 的顶层入口、`await` 的内部入口、`gather()` 的返回顺序都符合预期。

**坑**：在 Jupyter、Web 框架或已有事件循环中嵌套 `asyncio.run()`，通常会报事件循环已运行的错误；如果你只是为了在 `async def` 里调用另一个异步函数，直接 `await` 它。

**检查**：如果代码处在普通命令行脚本入口，用 `asyncio.run()`；如果代码已经在 `async def` 内，用 `await`。额外检查协程对象是否真的被 await/close，否则会留下 `RuntimeWarning: coroutine was never awaited`。
