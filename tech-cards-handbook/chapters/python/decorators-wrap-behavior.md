# 装饰器是在不改调用方的情况下包一层行为

**问题**：如何给函数统一增加日志、计时、权限检查等横切逻辑？

**要点**：

- 装饰器接收函数，返回一个替代函数。
- 包装函数要接收 `*args, **kwargs`，避免破坏原函数参数形状。
- 生产代码里通常要用 `functools.wraps` 保留原函数名称和文档。

**示例**：

```python
from functools import wraps


def announce(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"start {func.__name__}")
        result = func(*args, **kwargs)
        print(f"end {func.__name__}")
        return result
    return wrapper


@announce
def say_hello(name: str) -> str:
    return f"hello {name}"
```

**坑**：忘记 `return result` 会悄悄改变原函数返回值；忘记 `wraps` 会让调试、文档和测试报告变得混乱。

**检查**：装饰前后，函数的参数、返回值和异常语义是否一致？只应该增加你明确想增加的边界行为。
