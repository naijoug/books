# Proof output must be portable

## 问题

验证命令的输出经常会被复制到 notebook、最终报告、PR 描述或交接文档里。如果输出里混入本机绝对路径、临时目录、用户目录或不可复现的 runner 细节，下一轮 Agent 很难判断命令到底验证了什么，也容易把不该写入文档的环境信息带出去。

## 要点

- **执行命令可以用绝对路径，报告命令必须可移植。** wrapper 内部可以用完整路径调用脚本，但打印给人看的 step heading 应转换成 repo 相对路径。
- **先定义可复制边界。** 交接里优先出现 `python3 scripts/check.py`、`documents/...`、`books/...` 这类相对路径，而不是机器相关路径。
- **把 proof 当成将被复制的 artifact。** 如果命令输出会进入 `summaries/hermes/YYYY-MM-DD.md` 或最终响应，它就必须能被另一个 checkout 复用。
- **用回归测试守住输出格式。** 不只测试命令是否成功，还要测试 rendered command 不包含 repo root、用户目录或临时目录。
- **不要为了好看隐藏失败事实。** 可移植化只改展示层；实际执行参数、exit code、stderr 和失败文件仍要保留。

## 示例

一次 verifier wrapper 可以这样分层：

```python
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]


def printable_command(command: list[str]) -> str:
    rendered: list[str] = []
    for part in command:
        path = Path(part)
        if path.is_absolute():
            try:
                rendered.append(path.relative_to(ROOT).as_posix())
                continue
            except ValueError:
                if Path(part) == Path(sys.executable):
                    rendered.append(Path(part).name)
                    continue
        rendered.append(part)
    return " ".join(rendered)


command = [sys.executable, str(ROOT / "scripts" / "verify_links.py")]
print(f"== {printable_command(command)} ==", flush=True)
# subprocess.run(command, check=True, cwd=ROOT)
```

配套测试不要只断言函数返回字符串，还要断言不会泄漏 repo root：

```python
rendered = printable_command([sys.executable, str(ROOT / "scripts" / "verify_links.py")])
assert rendered.startswith(f"{Path(sys.executable).name} scripts/verify_links.py")
assert str(ROOT) not in rendered
```

## 反例 / 修正

反例：

```text
== /opt/homebrew/bin/python3 /Users/name/workspace/books/scripts/verify_links.py ==
verified links: 711 local link(s)
```

这条输出虽然真实，但下一轮 Agent 复制到记录里后会暴露本机路径，也无法直接在另一个 checkout 运行。

修正：

```text
== python3 scripts/verify_links.py ==
verified links: 711 local link(s)
```

如果失败信息必须包含文件位置，也优先使用 repo 相对路径：

```text
tech-cards-handbook/chapters/ai-agent/proof-output-must-be-portable.md:12: broken local link
```

## 坑

- 只替换 `sys.executable`，但脚本路径仍打印绝对路径。
- 为了去掉绝对路径，把执行命令也改成相对路径，导致 wrapper 在非预期 cwd 下失效；展示层和执行层应该分开。
- 只检查成功路径，没有测试失败输出是否仍用相对路径定位文件。
- 在 notebook 里手动改写输出，导致记录和真实命令不一致；应该让工具本身打印可复制输出。
- 把“无绝对路径”误解成“不要写任何路径”；相对路径是交接证据，不应该删掉。

## 检查

- wrapper 的 human-readable heading 是否只包含 repo 相对路径或可移植命令名？
- 回归测试是否断言 `str(ROOT) not in rendered`，并覆盖至少一个仓库内脚本路径？
- 失败输出是否仍能定位到相对文件和行号？
- notebook 或最终报告能否原样复制命令到同一 repo 的另一个 checkout 中运行？
- 如果输出会进入 `summaries/hermes/YYYY-MM-DD.md`，是否符合“只写相对路径”的记录规则？
