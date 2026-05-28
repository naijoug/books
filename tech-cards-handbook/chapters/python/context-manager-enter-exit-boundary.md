# 上下文管理器用于固定“进入/退出”边界

**问题**：什么时候写 `with` 或自定义 context manager？

**要点**：

- 适合成对操作：打开/关闭、加锁/解锁、开始事务/提交回滚。
- `with` 的价值是把失败路径也纳入退出逻辑。
- 简单场景用 `contextlib.contextmanager`，复杂状态用类。

**示例**：

```python
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from time import perf_counter
from typing import List


@contextmanager
def timer(label: str, events: List[str]):
    events.append(f"enter:{label}")
    start = perf_counter()
    try:
        yield events
    finally:
        elapsed = perf_counter() - start
        events.append(f"exit:{label}")
        print(f"{label}: {elapsed:.3f}s")


normal_events: List[str] = []
buffer = StringIO()
with redirect_stdout(buffer):
    with timer("load data", normal_events) as events:
        events.append("body:load data")
        data = [n * n for n in range(10)]

assert data[-1] == 81
assert normal_events == ["enter:load data", "body:load data", "exit:load data"]
assert buffer.getvalue().startswith("load data: ")

error_events: List[str] = []
try:
    with redirect_stdout(StringIO()):
        with timer("fail fast", error_events) as events:
            events.append("body:fail fast")
            raise ValueError("boom")
except ValueError as exc:
    assert str(exc) == "boom"
else:
    raise AssertionError("ValueError should propagate")

assert error_events == ["enter:fail fast", "body:fail fast", "exit:fail fast"]
```

**坑**：不要在 `finally` 中隐藏原始异常，除非你明确要转换异常类型；如果 `__exit__` 或 `contextmanager` 的退出段吞掉异常，调用方会误以为主体成功执行。

**检查**：把代码保存为 `context-manager-enter-exit-boundary.py` 后运行 `python3 context-manager-enter-exit-boundary.py`；正常路径应记录 `enter -> body -> exit`，异常路径也应记录 `exit`，且 `ValueError("boom")` 会继续向外传播。
