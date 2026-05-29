# Swift 技术卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 10 张。文件名使用英文 `kebab-case`。

| 卡片 | 文件 |
|---|---|
| Swift `struct` 适合值语义，`class` 适合共享身份 | [`swift-struct-value-class-identity.md`](swift-struct-value-class-identity.md) |
| Swift async/await 让异步流程保持顺序可读 | [`swift-async-await-readable-flow.md`](swift-async-await-readable-flow.md) |
| Swift 基础值优先用 `let` | [`swift-let-for-basic-values.md`](swift-let-for-basic-values.md) |
| Swift 字符串插值比拼接更清晰 | [`swift-string-interpolation.md`](swift-string-interpolation.md) |
| Swift 数组和字典都要处理“可能没有” | [`swift-array-dictionary-missing-values.md`](swift-array-dictionary-missing-values.md) |
| Swift `switch` 适合表达离散分支 | [`swift-switch-discrete-branches.md`](swift-switch-discrete-branches.md) |
| Swift 可选绑定替代强制解包 | [`swift-optional-binding-no-force-unwrap.md`](swift-optional-binding-no-force-unwrap.md) |
| Swift 闭包让行为可以作为参数传递 | [`swift-closures-as-parameters.md`](swift-closures-as-parameters.md) |
| Swift `defer` 把清理逻辑贴近资源获取 | [`swift-defer-for-cleanup.md`](swift-defer-for-cleanup.md) |
| Swift `Result` 把成功和失败放进同一个值 | [`swift-result-explicit-failure-state.md`](swift-result-explicit-failure-state.md) |

## 可运行验证进度

Swift 工具链已在本机确认可用（`swift --version`）。当前优先把示例改成可复制运行的小脚本；新增或改写卡片时，至少补一个 `swift <file>.swift` 或 `swiftc <file>.swift` 的检查命令。

| 卡片 | 验证方式 |
|---|---|
| [`swift-array-dictionary-missing-values.md`](swift-array-dictionary-missing-values.md) | `swift swift-array-dictionary-missing-values.swift` |
| [`swift-async-await-readable-flow.md`](swift-async-await-readable-flow.md) | `swift swift-async-await-readable-flow.swift` |
| [`swift-closures-as-parameters.md`](swift-closures-as-parameters.md) | `swift swift-closures-as-parameters.swift` |
| [`swift-defer-for-cleanup.md`](swift-defer-for-cleanup.md) | `swift swift-defer-for-cleanup.swift` |
| [`swift-let-for-basic-values.md`](swift-let-for-basic-values.md) | `swift swift-let-for-basic-values.swift` |
| [`swift-optional-binding-no-force-unwrap.md`](swift-optional-binding-no-force-unwrap.md) | `swift swift-optional-binding-no-force-unwrap.swift` |
| [`swift-result-explicit-failure-state.md`](swift-result-explicit-failure-state.md) | `swift swift-result-explicit-failure-state.swift` |
| [`swift-string-interpolation.md`](swift-string-interpolation.md) | `swift swift-string-interpolation.swift` |
| [`swift-struct-value-class-identity.md`](swift-struct-value-class-identity.md) | `swift swift-struct-value-class-identity.swift` |
| [`swift-switch-discrete-branches.md`](swift-switch-discrete-branches.md) | `swift swift-switch-discrete-branches.swift` |

## 章节级批量复核

从 `books` 仓库根目录运行下面的命令，可以抽取本章每张卡片里的 `swift` 代码块，并用本机 Swift 工具链逐个执行。预期输出最后一行是 `failures []`。

```bash
python3 - <<'PY'
from pathlib import Path
import os
import re
import subprocess
import tempfile

base = Path('tech-cards-handbook/chapters/swift')
failures = []

for path in sorted(base.glob('swift-*.md')):
    text = path.read_text()
    blocks = re.findall(r'```swift\n(.*?)\n```', text, re.S)
    if not blocks:
        failures.append((path.name, 'no swift blocks'))
        continue

    with tempfile.NamedTemporaryFile('w', suffix='.swift', delete=False) as handle:
        handle.write('\n\n'.join(blocks))
        temp_path = handle.name

    result = subprocess.run(['swift', temp_path], capture_output=True, text=True)
    os.unlink(temp_path)
    print(path.name, 'blocks', len(blocks), 'returncode', result.returncode)
    if result.returncode != 0:
        failures.append((path.name, result.stderr.strip()))

print('failures', failures)
PY
```
