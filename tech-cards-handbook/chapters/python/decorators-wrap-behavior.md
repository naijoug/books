# 装饰器是在不改调用方的情况下包一层行为

**问题**：如何给函数统一增加日志、计时、权限检查等横切逻辑？

**要点**：

- 装饰器接收函数，返回一个替代函数。
- 包装函数要接收 `*args, **kwargs`，避免破坏原函数参数形状。
- 生产代码里通常要用 `functools.wraps` 保留原函数名称和文档。

**示例**：

```python
from functools import wraps
from io import StringIO
from contextlib import redirect_stdout
from typing import Callable, TypeVar

R = TypeVar("R")


def announce(func: Callable[..., R]) -> Callable[..., R]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> R:
        print(f"start {func.__name__}")
        result = func(*args, **kwargs)
        print(f"end {func.__name__}")
        return result
    return wrapper


@announce
def say_hello(name: str) -> str:
    """Build a greeting."""
    return f"hello {name}"


buf = StringIO()
with redirect_stdout(buf):
    value = say_hello("Ada")

assert value == "hello Ada"
assert buf.getvalue().splitlines() == ["start say_hello", "end say_hello"]
assert say_hello.__name__ == "say_hello"
assert say_hello.__doc__ == "Build a greeting."
```

可以把代码保存为 `decorators-wrap-behavior.py`，执行：

```bash
python3 decorators-wrap-behavior.py
```

没有输出且退出码为 `0`，说明装饰器没有破坏返回值，也通过 `wraps` 保留了函数元数据。

**坑**：忘记 `return result` 会悄悄改变原函数返回值；忘记 `wraps` 会让调试、文档和测试报告变得混乱。类型标注里如果直接写 `Callable[..., R]`，只能保住返回值，参数形状仍会变宽；Python 3.10+ 或安装 `typing_extensions` 后，可以进一步用 `ParamSpec` + `TypeVar` 透传签名。

**检查**：装饰前后，函数的参数、返回值和异常语义是否一致？只应该增加你明确想增加的边界行为。至少用一个断言覆盖返回值，一个断言覆盖新增副作用，一个断言覆盖 `__name__`/`__doc__` 等元数据。
