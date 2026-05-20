# 带参数装饰器需要再多一层函数

**问题**：装饰器本身也需要配置项时，函数层级应该怎么写？

**要点**：

- 普通装饰器形状是 `decorator(func) -> wrapper`。
- 带参数装饰器形状是 `decorator_factory(option) -> decorator(func) -> wrapper`。
- 多个装饰器叠加时，离函数最近的装饰器先包裹。

**示例**：

```python
from functools import wraps


def repeat(times: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


@repeat(3)
def ping() -> str:
    print("ping")
    return "ok"
```

**坑**：把 `times` 写进全局变量会让装饰器不可复用；把层级写错会在导入阶段就执行原函数。

**检查**：读装饰器时按三层问自己：配置参数在哪里进入？原函数在哪里进入？调用参数在哪里进入？
