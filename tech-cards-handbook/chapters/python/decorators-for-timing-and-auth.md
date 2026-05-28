# 计时和权限检查适合做成装饰器

**问题**：哪些逻辑适合抽成装饰器，而不是散落在每个函数内部？

**要点**：

- 适合装饰器的逻辑通常与业务核心无关，但很多函数都需要。
- 常见例子包括计时、鉴权、重试、缓存、审计日志。
- 装饰器应保持小而明确，不要把复杂业务流程塞进去。

**示例**：

```python
import sys
from functools import wraps
from io import StringIO
from time import perf_counter


def timer(func):
    """Print elapsed time after each call."""
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
def build_report(rows: list) -> int:
    return len(rows)


# --- assertions ---
buf = StringIO()
sys.stdout = buf
result = build_report([{"id": 1}, {"id": 2}])
sys.stdout = sys.__stdout__

assert result == 2, f"expected 2, got {result}"
assert build_report.__name__ == "build_report", "@wraps should preserve __name__"
output = buf.getvalue()
assert "build_report took" in output, f"timer output missing: {output!r}"
assert output.strip().endswith("s"), f"timer output format wrong: {output!r}"
print("all checks passed")
```

> **验证**：保存为 `decorators-for-timing-and-auth.py`，运行 `python3 decorators-for-timing-and-auth.py`，应输出 `all checks passed`。
> 把 `@timer` 去掉后装饰器不再打印计时信息，但 `build_report([{}, {}])` 仍返回 `2`——证明业务逻辑独立于装饰器。

**坑**：装饰器如果吞掉异常或改变返回值，调用方会很难判断真实行为；除非目标就是错误转换，否则让异常自然抛出。

**检查**：把装饰器去掉后，业务逻辑是否仍然成立？如果不成立，说明装饰器可能承担了过多业务责任。
