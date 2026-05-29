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
| [`swift-defer-for-cleanup.md`](swift-defer-for-cleanup.md) | `swift swift-defer-for-cleanup.swift` |
| [`swift-optional-binding-no-force-unwrap.md`](swift-optional-binding-no-force-unwrap.md) | `swift swift-optional-binding-no-force-unwrap.swift` |
| [`swift-result-explicit-failure-state.md`](swift-result-explicit-failure-state.md) | `swift swift-result-explicit-failure-state.swift` |
| [`swift-string-interpolation.md`](swift-string-interpolation.md) | `swift swift-string-interpolation.swift` |
