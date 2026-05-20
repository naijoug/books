# 上下文管理器用于固定“进入/退出”边界

**问题**：什么时候写 `with` 或自定义 context manager？

**要点**：

- 适合成对操作：打开/关闭、加锁/解锁、开始事务/提交回滚。
- `with` 的价值是把失败路径也纳入退出逻辑。
- 简单场景用 `contextlib.contextmanager`，复杂状态用类。

**示例**：

```python
from contextlib import contextmanager
from time import perf_counter

@contextmanager
def timer(label: str):
    start = perf_counter()
    try:
        yield
    finally:
        elapsed = perf_counter() - start
        print(f"{label}: {elapsed:.3f}s")

with timer("load data"):
    data = [n * n for n in range(100_000)]
```

**坑**：不要在 `finally` 中隐藏原始异常，除非你明确要转换异常类型。

**检查**：人为在 `with` 块中抛异常，确认退出逻辑仍执行。
