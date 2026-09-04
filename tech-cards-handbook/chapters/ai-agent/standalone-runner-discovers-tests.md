# Standalone runner discovers tests

## 问题

很多仓库同时支持 `pytest` / CI 和“直接运行单个测试文件”的 standalone runner。Agent 在补回归测试时，常把文件底部的 `if __name__ == "__main__"` 写成手工函数清单：新增 `test_*` 后忘记同步清单，直接运行仍显示 `ok`，但新 case 实际没有执行。这个问题不是测试数量少，而是验证入口会静默跳过最新风险。

## 要点

- **先识别 runner 是否是契约入口。** 如果 README、`scripts/check.sh`、CI fallback 或 cron handoff 会执行 `python3 tests/test_x.py`，文件底部 runner 就是交付契约，不只是开发便利。
- **手写清单只适合固定场景脚本。** 当同一文件里的 `test_*` 会继续增长，优先自动发现本模块 callable，并按源码行号执行，避免新增测试被漏进 runner。
- **发现范围要窄。** 只扫描当前模块 `globals()` 中命名为 `test_` 的 callable；不要跨文件递归，也不要模拟 pytest fixture、parametrize 或 marker。
- **输出测试数量。** 成功消息包含实际执行数量，例如 `module regression tests ok: 7 test(s)`；这样下一轮改动能从输出里发现 case 数是否变化。
- **不适用时写明原因。** 如果测试依赖 pytest fixture、monkeypatch、临时目录 fixture 或异步 test plugin，就不要硬改 standalone runner；改为在 runner 旁注释“use pytest”，或让 shell 入口调用 pytest。

## 示例

```python
from collections.abc import Callable
from typing import cast


def _standalone_tests() -> list[Callable[[], None]]:
    tests = [
        cast(Callable[[], None], value)
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    ]
    return sorted(tests, key=lambda fn: fn.__code__.co_firstlineno)


if __name__ == "__main__":
    tests = _standalone_tests()
    for test in tests:
        test()
    print(f"invoice parser regression tests ok: {len(tests)} test(s)")
```

配套验证不是只看退出码：

```text
Focused proof:
python3 tests/test_invoice_parser.py
# invoice parser regression tests ok: 7 test(s)

Drift proof:
git diff --check -- tests/test_invoice_parser.py

Handoff:
runner auto-discovers same-file test_* callable by source order; if future cases need pytest fixtures, switch this entry to pytest instead of extending custom discovery.
```

## 坑

- 只把清单改成列表推导，却没有按源码行号排序；下一轮输出顺序可能跟插入顺序或动态导入细节耦合。
- 自动发现跨模块测试，导致 standalone runner 变成半个测试框架，fixture、环境变量和慢测试边界都不清楚。
- 成功消息仍写死旧数量，让 notebook 里看不出 runner 是否真的执行了新增 case。
- 看到 pytest fixture 仍强行 `test()`，结果为了让 standalone 通过而删掉更有价值的 fixture 语义。
- 只跑 standalone 文件，不跑调用它的 `scripts/check.sh` 或仓库 preflight，漏掉 shell 入口仍指向旧命令的问题。

## 检查

提交前逐条确认：这个文件是否确实有 standalone 入口；`test_*` 自动发现是否只限当前模块 callable；执行顺序是否按 `co_firstlineno`；成功输出是否包含实际数量；是否跑过文件本身、上层 check 脚本和 `git diff --check`；如果不适用自动发现，是否在 runner 或交接里写清必须用 pytest 的原因。
