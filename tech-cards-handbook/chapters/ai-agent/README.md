# AI Agent 系统实践卡片

本目录按"一张卡片一个 Markdown 文件"维护,共 38 张。文件名使用英文 `kebab-case`。

本目录收录 Agent 系统设计、运行边界、工具、记忆、反馈判断、反馈池和心跳工作流等实践卡片;具体 SDK 或语言实现优先放入对应技术栈目录。

本章不纳入 `scripts/verify_all_cards.py --language ...` 的语言代码 verifier;维护时以 `chapters/README.md` 的索引校验和链接校验为准,并人工复核每张卡片是否仍包含问题、要点、示例、坑、检查五段。

如果读者正在处理"周期性唤醒的 Agent + 已有 dirty workspace + 多 repo 接力"这类场景,优先使用 [`../../samples/ai-agent-dirty-workspace-one-pager.md`](../../samples/ai-agent-dirty-workspace-one-pager.md),再按下面的运行控制顺序深入阅读。

## 3 分钟读法

如果只想马上减少一次心跳接力的事故率,先按三条线读,不要从 38 张卡片顺序扫完:

1. **失败吸收线**:读 [`failure-output-must-change-plan.md`](failure-output-must-change-plan.md),再用 [`../../samples/ai-agent-failure-absorption-one-pager.md`](../../samples/ai-agent-failure-absorption-one-pager.md) 记录`信号 -> 影响 -> 证据位置`,确认失败是否改变了范围、顺序、目标或交接。
2. **dirty workspace 线**:读 [`startup-snapshot-before-planning.md`](startup-snapshot-before-planning.md)、[`uncommitted-handoff-needs-ownership-triage.md`](uncommitted-handoff-needs-ownership-triage.md) 和 [`staged-changes-are-not-ownership.md`](staged-changes-are-not-ownership.md),先分清启动前改动、staged path、可接管 path,再决定本轮文件范围。
3. **提交证据线**:读 [`commit-scope-ledger-prevents-mixed-ownership.md`](commit-scope-ledger-prevents-mixed-ownership.md)、[`dirty-workspace-exit-checklist.md`](dirty-workspace-exit-checklist.md) 和 [`report-from-committed-state.md`](report-from-committed-state.md),最终报告从已提交状态读回 hash,同时写清排除边界；收尾前可用 [`../../samples/ai-agent-final-report-field-quickref.md`](../../samples/ai-agent-final-report-field-quickref.md) 核对固定字段，若验证失败或无法执行，再用 [`../../samples/ai-agent-verification-failure-handoff-template.md`](../../samples/ai-agent-verification-failure-handoff-template.md) 把可信结论、未验证项和下一步第一条动作拆开。

完成这三条线后,再进入下面的 13 步快速路径补齐运行控制细节。

## 快速路径:dirty workspace 心跳接力

这条路径不是通用入门顺序,而是给已经在真实项目里工作的 Agent 使用:先建立启动快照,把上一轮接力点当作信号而不是义务,再选择可安全推进的小任务,最后把成果和未接管边界同时写清。

| 步骤 | 阶段 | 目标 | 卡片 |
|---|---|---|---|
| 1 | 唤醒与事实 | 防止凭上一轮印象行动 | [`heartbeat-workflow-prevents-drift.md`](heartbeat-workflow-prevents-drift.md) |
| 2 | 唤醒与事实 | 在规划前保存当前 repo 状态 | [`startup-snapshot-before-planning.md`](startup-snapshot-before-planning.md) |
| 3 | 规划与取舍 | 从候选工作中做取舍 | [`planning-selects-work-not-just-summary.md`](planning-selects-work-not-just-summary.md) |
| 4 | 规划与取舍 | 把上一轮接力点当作信号,而不是自动义务 | [`continuation-is-signal-not-obligation.md`](continuation-is-signal-not-obligation.md) |
| 5 | 规划与取舍 | 无人值守时选择低风险默认动作,而不是等待澄清 | [`unattended-agent-chooses-default-action.md`](unattended-agent-chooses-default-action.md) |
| 6 | 规划与取舍 | 让失败输出改变范围、顺序、目标或交接 | [`failure-output-must-change-plan.md`](failure-output-must-change-plan.md) |
| 7 | 所有权边界 | 对启动前 dirty 接力文件做归属判断;最终报告保留状态证据 | [`uncommitted-handoff-needs-ownership-triage.md`](uncommitted-handoff-needs-ownership-triage.md) |
| 8 | 所有权边界 | 单独识别启动前 staged path,不把 index 状态误当授权;状态证据必须进入最终报告 | [`staged-changes-are-not-ownership.md`](staged-changes-are-not-ownership.md) |
| 9 | 所有权边界 | 用提交范围台账防止混入未知归属;台账包含状态证据列 | [`commit-scope-ledger-prevents-mixed-ownership.md`](commit-scope-ledger-prevents-mixed-ownership.md) |
| 10 | 收尾与状态证据 | 用清单做 path-limited 收尾 | [`dirty-workspace-exit-checklist.md`](dirty-workspace-exit-checklist.md) |
| 11 | 收尾与状态证据 | 先跑聚焦验证并显式交接未验证项 | [`verify-before-optimistic-summary.md`](verify-before-optimistic-summary.md)、[`unverified-items-need-explicit-handoff.md`](unverified-items-need-explicit-handoff.md) |
| 12 | 报告与读回 | 从已提交状态读回 hash 和 subject;报告包含启动/收尾状态证据 | [`report-from-committed-state.md`](report-from-committed-state.md) |
| 13 | 报告与读回 | 最终响应同时列成果和排除项 | [`final-report-names-excluded-boundaries.md`](final-report-names-excluded-boundaries.md) |

失败吸收线索：步骤 6 不是事后解释失败，而是要求失败输出立刻改变范围、顺序、目标或交接；可先读 [`failure-output-must-change-plan.md`](failure-output-must-change-plan.md)，再用 [`../../samples/ai-agent-failure-absorption-one-pager.md`](../../samples/ai-agent-failure-absorption-one-pager.md) 做收尾检查，并对照 [`../../samples/ai-agent-sample-pack.md`](../../samples/ai-agent-sample-pack.md) 中“失败吸收速记”的四类最小改计划例子，检查最终 notebook 是否写清“失败如何改变了本轮选择”。

状态证据线索：步骤 7–9 和 12 的卡片已在 2026-06-25 补强，要求最终报告保留启动/收尾 `git status --short`、分 repo 读回 commit hash、提交范围台账包含状态证据列；读者可按这条线索从所有权边界串到最终报告，并用 [`../../samples/ai-agent-sample-pack.md`](../../samples/ai-agent-sample-pack.md) 的样本包、[`../../samples/ai-agent-dirty-workspace-one-pager.md`](../../samples/ai-agent-dirty-workspace-one-pager.md) 的一页纸和 [`../../samples/ai-agent-final-report-field-quickref.md`](../../samples/ai-agent-final-report-field-quickref.md) 的字段速查核对可复制输入是否同步。

配套可复制输入见 [`../../samples/ai-agent-sample-pack.md`](../../samples/ai-agent-sample-pack.md) 的 dirty workspace 心跳交接样例；若只需要收尾核对，先读 [`../../samples/ai-agent-dirty-workspace-one-pager.md`](../../samples/ai-agent-dirty-workspace-one-pager.md) 和 [`dirty-workspace-exit-checklist.md`](dirty-workspace-exit-checklist.md)，再按"验证证据 -> 状态证据 -> 已提交状态读回 -> 排除边界"的顺序把启动/收尾 `git status --short` 摘要和 [`final-report-names-excluded-boundaries.md`](final-report-names-excluded-boundaries.md) 的最终响应模板填完整。

## 阅读顺序

### 1. 先确定 Agent 的边界

| 卡片 | 文件 |
|---|---|
| Agent 是模型、工具、循环和边界的组合 | [`agent-model-tool-loop-boundaries.md`](agent-model-tool-loop-boundaries.md) |
| 第一个 Agent 先做研究助手,不要一开始做全能助手 | [`first-agent-research-assistant.md`](first-agent-research-assistant.md) |

### 2. 再打磨工具和上下文

工具两张卡建议按"调用前契约 → 调用后证据"的顺序阅读:先用工具描述写清使用场景、输入边界和不可用条件,再用可观察工具结果让下一轮能判断实际变化、证据位置和下一步验证。

上下文三张卡建议按"事实来源 → 预算筛选 → 状态分层"的顺序阅读:先确认记忆不能替代权威事实,再决定哪些材料值得进入本轮上下文,最后把长期身份、项目事实、工具结果和未验证假设拆成可更新、可失效、可写回的状态层。

| 卡片 | 文件 |
|---|---|
| 工具描述要写用途和输入,不要只写名字 | [`tool-descriptions-use-case-input.md`](tool-descriptions-use-case-input.md) |
| 工具结果必须可观察,不要只返回"成功" | [`tool-result-must-be-observable.md`](tool-result-must-be-observable.md) |
| 记忆用于延续上下文,不是事实唯一来源 | [`memory-is-context-not-source-of-truth.md`](memory-is-context-not-source-of-truth.md) |
| 上下文预算是一种资源,不要把所有历史都塞进提示 | [`context-budget-is-a-resource.md`](context-budget-is-a-resource.md) |
| 上下文工程是状态设计,不是把材料拼成长提示 | [`context-engineering-is-state-design.md`](context-engineering-is-state-design.md) |

### 3. 建立反馈和运行控制

反馈闭环建议按"事实/推断分离 → 有效反馈升级 → 反馈池字段化"的顺序阅读:先避免把感受直接写成结论,再判断信号是否足以触发修订,最后把仍需观察的反馈留成可复查字段。

运行控制建议按"失败出口 → 心跳闭环 → 可执行交接 → 验证与报告"的顺序阅读:先给 Agent 设置停止条件,再用心跳维持长期任务节奏;每次交接都写清下一步动作,并用验证、显式未验证项和已提交状态约束最终报告。若正在处理 dirty workspace 心跳接力,以本页顶部"快速路径"的顺序为准;下面表格是通用主题目录,不要把失败输出、staged 归属或验证交接延后到收尾时才判断。

| 卡片 | 文件 |
|---|---|
| 反馈必须区分事实和推断,不要把感觉当结论 | [`feedback-must-separate-facts-and-inferences.md`](feedback-must-separate-facts-and-inferences.md) |
| 有效反馈才触发修订,不要被每个声音牵着走 | [`validated-feedback-triggers-revision.md`](validated-feedback-triggers-revision.md) |
| 反馈池要把信号留成可执行字段 | [`feedback-pool-keeps-signals-actionable.md`](feedback-pool-keeps-signals-actionable.md) |
| Agent 必须有迭代上限和失败出口 | [`agent-iteration-limit-failure-exit.md`](agent-iteration-limit-failure-exit.md) |
| 心跳工作流让长期任务不漂移 | [`heartbeat-workflow-prevents-drift.md`](heartbeat-workflow-prevents-drift.md) |
| 启动快照先于规划,不要凭上一轮印象选任务 | [`startup-snapshot-before-planning.md`](startup-snapshot-before-planning.md) |
| 规划要选择工作,不要只复述状态 | [`planning-selects-work-not-just-summary.md`](planning-selects-work-not-just-summary.md) |
| 交接必须写下一步动作,不要只写状态 | [`handoff-must-name-next-action.md`](handoff-must-name-next-action.md) |
| 接力点是信号,不是义务 | [`continuation-is-signal-not-obligation.md`](continuation-is-signal-not-obligation.md) |
| 无人值守 Agent 要选择默认动作,不要等待澄清 | [`unattended-agent-chooses-default-action.md`](unattended-agent-chooses-default-action.md) |
| 未提交接力文件先判断归属,不要直接接管 | [`uncommitted-handoff-needs-ownership-triage.md`](uncommitted-handoff-needs-ownership-triage.md) |
| Staged 改动不等于本轮所有权 | [`staged-changes-are-not-ownership.md`](staged-changes-are-not-ownership.md) |
| 提交范围台账防止混入未知归属 | [`commit-scope-ledger-prevents-mixed-ownership.md`](commit-scope-ledger-prevents-mixed-ownership.md) |
| 短节拍任务不要变成重构 | [`short-cadence-tasks-must-not-become-refactors.md`](short-cadence-tasks-must-not-become-refactors.md) |
| 验证先于乐观总结,不要把"看起来完成"当完成 | [`verify-before-optimistic-summary.md`](verify-before-optimistic-summary.md) |
| 未验证项要显式交接,不要藏在顺利总结里 | [`unverified-items-need-explicit-handoff.md`](unverified-items-need-explicit-handoff.md) |
| 最终报告要来自已提交状态,不要来自计划中的状态 | [`report-from-committed-state.md`](report-from-committed-state.md) |
| 最终报告要写清排除边界,不要只报完成项 | [`final-report-names-excluded-boundaries.md`](final-report-names-excluded-boundaries.md) |
| Dirty workspace 收尾要有清单,不要靠最后一眼状态 | [`dirty-workspace-exit-checklist.md`](dirty-workspace-exit-checklist.md) |
| 失败输出要改变计划,不要当作背景噪音 | [`failure-output-must-change-plan.md`](failure-output-must-change-plan.md) |
| AI 编程审查要先做固定范围 offer,不要一上来卖全栈自动化 | [`ai-coding-audit-is-fixed-scope-offer.md`](ai-coding-audit-is-fixed-scope-offer.md) |
| 先交付首份报告，不要先卖咨询 | [`first-report-before-consulting.md`](first-report-before-consulting.md) |
| 先跑 30 分钟路线，不要先产品化 | [`thirty-minute-route-before-productizing.md`](thirty-minute-route-before-productizing.md) |
| AI 生成 PR 需要单独审查入口,不要混进普通代码审查 | [`ai-generated-pr-needs-review-entry.md`](ai-generated-pr-needs-review-entry.md) |
| AI 辅助 PR 审查路径要像产品阶梯,不要只是一组文章 | [`ai-assisted-pr-review-path-is-product-ladder.md`](ai-assisted-pr-review-path-is-product-ladder.md) |
| 下一条安全命令梯不是测试清单，不要只写“再跑一遍” | [`next-safe-command-ladder-is-not-test-list.md`](next-safe-command-ladder-is-not-test-list.md) |
| 匿名案例不能编造证据，不要把样板写成战报 | [`anonymous-case-must-not-invent-evidence.md`](anonymous-case-must-not-invent-evidence.md) |
| 公开案例先分事实、推断和未验证，不要把审查记录直接写成结论 | [`public-case-separates-facts-inferences-unverified.md`](public-case-separates-facts-inferences-unverified.md) |
| Repo 里的 Agent 规则要有可见入口,不要只藏在聊天记录里 | [`repo-agent-rules-need-visible-entry.md`](repo-agent-rules-need-visible-entry.md) |

### 4. 最后抽象为助手操作系统

| 卡片 | 文件 |
|---|---|
| AI 助手操作系统先分清身份、用户、工具和心跳 | [`assistant-os-layers.md`](assistant-os-layers.md) |
| 启动层只负责初始化,不应该长期参与运行 | [`bootstrap-is-initialization-only.md`](bootstrap-is-initialization-only.md) |
