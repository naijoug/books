# 计时和权限检查适合做成装饰器

**问题**：哪些逻辑适合抽成装饰器，而不是散落在每个函数内部？

**要点**：

- 适合装饰器的逻辑通常与业务核心无关，但很多函数都需要。
- 常见例子包括计时、鉴权、重试、缓存、审计日志。
- 装饰器应保持小而明确，不要把复杂业务流程塞进去。

**示例**：

```python
from functools import wraps
from time import perf_counter


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        started = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = perf_counter() - started
            print(f"{func.__name__} took {elapsed:.3f}s")
    return wrapper


@timer
def build_report(rows: list[dict]) -> int:
    return len(rows)
```

**坑**：装饰器如果吞掉异常或改变返回值，调用方会很难判断真实行为；除非目标就是错误转换，否则让异常自然抛出。

**检查**：把装饰器去掉后，业务逻辑是否仍然成立？如果不成立，说明装饰器可能承担了过多业务责任。
