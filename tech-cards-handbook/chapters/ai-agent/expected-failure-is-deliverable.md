# Expected Failure 也是交付物

**问题**：Agent 在阶段性任务里经常遇到“结构校验已绿，但 release gate 仍红”“权限 gate 正确阻断”“覆盖率门禁暂时不该通过”。如果只在报告里写“还有失败”，下一轮很容易为了追绿误改门禁、跳过授权或降低质量阈值。怎样把预期失败写成可交付的契约，让红灯也能指导下一步？

**要点**：

- 先判断失败是否真的“预期”：它必须来自当前阶段尚未满足的明确 gate，而不是未知异常、环境漂移或测试脆弱。
- 用五个字段描述：`Scope`（只在哪个阶段/命令下允许红）、`Reason`（为什么现在应当红）、`Allowed signal`（允许出现的错误码、stderr 关键词或状态）、`Stop signal`（一旦出现就必须停）、`Next safe command`（下一轮第一条安全动作）。
- 把 expected failure 和 green proof 并列交付：例如 draft manifest 结构校验通过是 green proof，release coverage 不足是 expected failure；不要用红灯覆盖已完成的绿灯。
- 失败契约要贴近命令输出，而不是散文解释；下一轮应能根据同一条命令判断“仍在预期范围内”还是“已经变成新问题”。
- 解除 expected failure 必须有新的事实输入：内容覆盖补齐、授权字段补齐、外部链接可用、全量基线变绿；不能靠降低 gate、改断言文案或跳过检查。

**示例**：

```text
Scenario:
内容型产品正在导入教材草稿。本轮只承诺生成 draft manifest、排序、来源和结构校验；整册 release 覆盖率尚未完成。

Green proof:
python3 scripts/content/validate-draft-manifest.py content/materials/pep/chinese/grade-3-upper.json
=> draft manifest ok: units sorted, source pages mapped, required fields present

Expected failure contract:
Scope: 只允许 `npm run content:release-check -- pep/chinese/grade-3-upper` 红。
Reason: 第三单元后续 practice/review 尚未补齐，release coverage gate 应继续阻断发布。
Allowed signal: exit 非 0，stderr 包含 `missing release-ready materials` 与缺失 unit id。
Stop signal: 结构校验红、缺失来源页、release check 变绿但 manifest 未覆盖全部 unit、或错误变成 parser exception。
Next safe command: 先补一个缺失 unit 的 draft material，再重跑 draft manifest validator 和 release check。

Handoff:
不要为追绿修改 release gate；下一轮只在内容覆盖补齐后解除 expected failure。
```

**反例 / 修正做法**：

```text
反例：
- “测试失败是正常的，后面再看。”没有命令、允许信号和停止信号。
- 为了让 CI 绿，把 release gate 改成忽略 draft 状态。
- 把所有红灯都叫 expected failure，包括 parser 崩溃、权限异常和 fixture 缺失。
- 只报告 expected failure，不报告本轮实际变绿的结构 proof。

修正：
- 每个 expected failure 只绑定一条 gate 或一类命令输出。
- 写清哪种红灯仍可继续、哪种红灯必须停。
- 下一轮必须先执行 `Next safe command`，而不是直接扩大重构或跳过 gate。
```

**坑**：

- **把预期失败当免责条款**：expected failure 不是“失败也算完成”，而是把阶段边界写成可验证契约。
- **允许信号太宽**：只写“命令失败”会把 parser panic、网络故障和真实覆盖缺口混在一起。
- **停止信号缺失**：没有 stop signal 时，下一轮无法知道何时该改变计划。
- **绿灯与红灯混淆**：某个 gate 应该红，不代表本轮没有可交付成果；必须同时写清已绿 proof。
- **解除条件不可证实**：如果只写“后续完善后解除”，下一轮仍不知道该补哪个事实。

**检查**：提交前逐条问：这次红灯是否绑定了具体 gate；`Scope / Reason / Allowed signal / Stop signal / Next safe command` 是否齐全；是否保留了本轮 green proof；是否明确禁止靠降低门禁解除；下一轮是否能用同一条命令复判状态。任一项缺失，就不要把失败称为 expected failure。
