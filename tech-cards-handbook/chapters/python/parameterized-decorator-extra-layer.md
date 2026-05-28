# 带参数装饰器需要再多一层函数

**问题**：装饰器本身也需要配置项时，函数层级应该怎么写？

**要点**：

- 普通装饰器形状是 `decorator(func) -> wrapper`。
- 带参数装饰器形状是 `decorator_factory(option) -> decorator(func) -> wrapper`。
- 多个装饰器叠加时，离函数最近的装饰器先包裹。

**示例**：

```python
from contextlib import redirect_stdout
from functools import wraps
from io import StringIO
from typing import Callable, TypeVar

R = TypeVar("R")
events: list[str] = []


def repeat(times: int) -> Callable[[Callable[..., R]], Callable[..., R]]:
    events.append(f"factory({times})")

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        events.append(f"decorate({func.__name__})")

        @wraps(func)
        def wrapper(*args, **kwargs):
            events.append(f"call({func.__name__})")
            result = None
            for index in range(times):
                events.append(f"run({index + 1})")
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(3)
def ping() -> str:
    """Return a heartbeat."""
    print("ping")
    return "ok"


buffer = StringIO()
with redirect_stdout(buffer):
    result = ping()

assert result == "ok"
assert buffer.getvalue().splitlines() == ["ping", "ping", "ping"]
assert ping.__name__ == "ping"
assert ping.__doc__ == "Return a heartbeat."
assert events == [
    "factory(3)",
    "decorate(ping)",
    "call(ping)",
    "run(1)",
    "run(2)",
    "run(3)",
]
```

把代码保存为 `parameterized-decorator-extra-layer.py` 后运行：

```bash
python3 parameterized-decorator-extra-layer.py
```

没有输出且退出码为 0，说明三层函数的进入时机、重复调用次数和 `wraps` 元数据保留都符合预期。

**坑**：把 `times` 写进全局变量会让装饰器不可复用；把层级写错会在导入阶段就执行原函数；如果要精确保留参数签名，Python 3.10+ 可用 `ParamSpec`，Python 3.9 项目需要 `typing_extensions`。

**检查**：读装饰器时按三层问自己：配置参数在哪里进入？原函数在哪里进入？调用参数在哪里进入？再用事件列表断言导入期只发生 `factory/decorate`，调用期才发生 `call/run`。
