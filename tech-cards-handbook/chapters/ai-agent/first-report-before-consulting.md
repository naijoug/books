# 先交付首份报告，不要先卖咨询

## 问题

AI 编程审查的收入实验很容易从一个样本回复跳到“长期顾问、团队培训、全流程改造”。这会让买家还没看到你的判断能力，就先面对大范围承诺和高沟通成本。

更稳的路径是：拿到样本后先交付一份 30-60 分钟可完成的首份报告。首份报告只回答一个问题：基于当前证据，下一步最安全、最值得做的动作是什么？

## 要点

- **先证明判断力，再讨论服务形态**：首份报告是最小信任样本，不是咨询合同。它应该让对方看到你能区分事实、推断、未验证项和停止边界。
- **范围只读且短**：输入限定为一个 PR、一次 agent final report、一段失败日志或一条命令链；不要接生产权限、密钥、客户数据或大范围仓库改造。
- **输出压缩到 1 页**：包含 `Scope`、`Highest Risk`、`Evidence inspected`、`Next Safe Command Ladder`、`Unverified items` 和 `Continue / Narrow / Stop`；可直接复用 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md) 的字段骨架。
- **用证据决定升级**：只有当对方愿意补第二段证据、允许匿名复盘或明确询问模板化交付时，才讨论 paid audit、团队 checklist、PR template 或 agent skill。
- **材料不足时主动缩小**：如果样本只支持一个判断，就交付命令梯或证据边界片段；如果缺授权、脱敏或最小证据，就 `Stop`，不要用想象补全案例。

## 示例

```text
收到样本后不要这样回复：
我可以帮你们设计一整套 AI 编程工作流，包括工具选型、提示词、CI、review 规范和培训。

更好的首次回复：
我先做一份只读首份报告，只覆盖这次 agent 改动的最高风险点。
需要你提供：
1. 这次改动目标；
2. 最能代表卡点的 PR / log / final report / failed command；
3. 哪些内容不能公开或需要脱敏。

交付物：
- Scope / Excluded；
- Highest Risk + Evidence；
- Next Safe Command Ladder；
- Unverified items；
- Continue / Narrow / Stop。

模板：books/tech-cards-handbook/samples/ai-agent-audit-report-one-pager.md
```

首份报告的收尾可以这样写：

```text
Decision: Narrow
Reason: 当前只有 failed command 和口头描述，缺少 diff 或 final report，不能判断整体工作流质量。
Delivered: 下一条安全命令梯 + 需要补充的证据列表。
Next evidence needed: PR diff、agent final report、CI 配置或 reviewer comment 中任选一项。
```

这样即使没有升级成咨询，也留下了可信交付和下一步证据需求。

如果要把首份报告交给真实买家或下一轮 Agent，先复制 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md)，只填已检查证据；无法落到 `Top Risks` 或 `Next Safe Command Ladder` 的判断，放进 `Unverified items`，不要混进结论。

## 坑

- **把首份报告写成销售提案**：对方还没有验证你的判断力时，过早卖长期改造会增加决策阻力。
- **为了显得有价值而扩大范围**：第一次就覆盖整个 repo、团队流程和工具链，反而更难交付可复核结论。
- **没有停止条件**：样本缺授权、缺证据或含敏感数据时还继续写，会把方法论变成不可信案例。
- **只写建议不写证据**：报告里没有 `Evidence inspected` 和 `Unverified items`，读者无法判断哪些建议可执行。
- **把免费样本无限延长**：首份报告之后必须进入 `Continue / Narrow / Stop`，否则会变成无边界免费咨询。

## 检查

交付前检查：输入是否能在 10 分钟内准备；审查是否只读；报告是否压缩到 1 页；是否已经用 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md) 或等价字段补齐 `Scope`、`Evidence inspected`、`Top Risks`、`Next Safe Command Ladder`、`Unverified items`；每个关键判断是否有 `Fact`、`Inference`、`Unverified` 或 `Stop` 标签；是否写清 `Next evidence needed`；收尾是否明确 `Continue / Narrow / Stop`。只有 `Continue` 有新证据或明确购买意愿时，才进入咨询、模板化或产品化讨论。
