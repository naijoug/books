# `asyncio.run()` 是异步程序的同步入口

**问题**：什么时候用 `asyncio.run()`，什么时候只写 `await`？

**要点**：

- `async def` 只是在定义协程函数，调用后得到协程对象，并不会立刻执行。
- 顶层脚本通常用 `asyncio.run(main())` 启动事件循环。
- 已经在事件循环内部时，不要再调用 `asyncio.run()`，应该直接 `await`。

**示例**：

```python
import asyncio

async def make_coffee() -> str:
    await asyncio.sleep(2)
    return "coffee"

async def make_toast() -> str:
    await asyncio.sleep(1)
    return "toast"

async def main() -> None:
    coffee, toast = await asyncio.gather(make_coffee(), make_toast())
    print(coffee, toast)

if __name__ == "__main__":
    asyncio.run(main())
```

**坑**：在 Jupyter、Web 框架或已有事件循环中嵌套 `asyncio.run()`，通常会报事件循环已运行的错误。

**检查**：如果代码处在普通命令行脚本入口，用 `asyncio.run()`；如果代码已经在 `async def` 内，用 `await`。
