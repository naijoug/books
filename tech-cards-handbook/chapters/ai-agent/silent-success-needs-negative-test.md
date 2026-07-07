# 静默成功需要反向测试

**问题**：CLI、proof checker 或 Agent wrapper 遇到无效输入时仍然返回成功，下一轮就会把“什么都没检查”误读成“检查通过”。怎样在短节拍里发现并修掉这种静默成功？

**要点**：

- 先写 `Human hypothesis before agent`：哪个无效输入不应该通过、应该返回什么 exit code、错误消息必须包含哪些支持项。
- 给每个“可选过滤器 / 路径选择器 / 模式开关”至少补一个反向测试：未知值、空集合、被排除后无目标、拼错参数都不能静默成功。
- 成功输出必须说明检查了什么；失败输出必须说明为什么失败和下一步可用值。只有 `ok`、`passed` 或 `checked 0` 都不足以交接。
- 先补最小 CLI 回归测试，再跑一条真实命令观察 exit code 和 stderr/stdout；不要只 mock 内部函数。
- 如果反向测试会暴露已有用户工作区的脏文件，先用提交范围台账限定本轮 path，再在 notebook 里写清未接管边界。

**示例**：

```text
Observation:
- python3 scripts/verify_all_cards.py --language TypoScript 曾可能因为没有匹配语言而跑 0 个 verifier 后成功。

Human hypothesis before agent:
- 未知 --language 值应该是调用者错误，而不是空集合成功。
- 最小修复：在 argparse 阶段比较输入语言和支持语言集合；未知值 parser.error，exit 2。
- 错误消息必须包含未知值和 Supported languages。

Negative test:
- patch subprocess runner，断言 unknown language 不会调用任何 verifier。
- 真实命令：python3 scripts/verify_all_cards.py --language TypoScript

Expected output contract:
- exit code = 2
- stderr/stdout 含 unknown --language value(s): typoscript
- stderr/stdout 含 Supported languages: Flutter, Go, Python, React, Rust, Swift, TypeScript
```

**反例 / 修正做法**：

```text
反例：
- 只跑 python3 scripts/verify_all_cards.py --language Python，看到通过后总结“language 参数可用”。

问题：
- 正向测试只能证明已知值能跑，不能证明拼错值不会静默跳过。
- 对 Agent 接力而言，静默成功比失败更危险，因为后续报告会引用一个没有检查内容的 proof。

修正：
- 每新增一个过滤参数，同步写一条“拼错值必须失败”的测试。
- 每新增一个 exclude/list-files 参数，同步写一条“排除后无检查对象不能成功”的测试。
- 最终报告引用真实命令的 exit code 和错误消息，而不是只写“已补参数校验”。
```

**坑**：

- 把 `checked 0 file(s)`、`0 languages passed` 或空输出当成功；这通常意味着选择器没有命中目标。
- 只验证 happy path，忘记拼写错误、大小写归一化、重复值和 alias 这些调用者最容易犯错的输入。
- 错误消息只说 `invalid choice`，但不列出支持项；下一轮还要读源码才能修命令。
- 反向测试只测 helper 函数，不测 CLI exit code；真实 shell/argparse 行为仍可能不同。
- 失败后顺手重构整套 wrapper；短节拍里先让无效输入 fail fast，再决定是否值得整理结构。

**检查**：这轮改动结束时，至少能指出一条无效输入命令、它的非零 exit code、错误消息中的支持项，以及一条正向命令仍然通过。如果这些证据缺失，就不能把静默成功风险标记为已关闭。
