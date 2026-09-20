# AI Agent 系统实践卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 92 张。文件名使用英文 `kebab-case`。

每张卡片解决一个工程问题。先选择当前任务的入口，需要背景时再查看目录；书中示例流程不自动成为所在项目的执行规则。

## 本章四条主线

| 主线 | 任务 | 先打开 |
|---|---|---|
| 运行控制 | 接续已有任务、处理 dirty workspace | [心跳接力一页纸](../../samples/ai-agent-dirty-workspace-one-pager.md) |
| 验证与证据 | 确定本轮需要什么验证 | [验证入口决策表](../../samples/ai-agent-proof-to-preflight-decision-table.md) |
| 所有权与交付 | 判断已有改动能否继续或纳入提交 | [目标文件归属判断](dirty-target-file-blocks-continuation.md) |
| 产品化阶梯 | 交付固定范围的 AI 编程审查 | [审查报告一页纸](../../samples/ai-agent-audit-report-one-pager.md) |

## 3 分钟读法

只选与当前问题匹配的一行，完成其中的动作；无需把四条主线和全部卡片依次读完。需要其他场景时查 [样本索引](../../samples/README.md)。

- 用户已指定任务：围绕该目标推进；归属清晰、能够保留已有 diff 时可继续修改。
- 文件冲突或归属不明：只暂停受影响部分，先完成原任务内独立工作；跨项目另选任务须已获授权。
- 需要完整可复制输入：打开 [样本包](../../samples/ai-agent-sample-pack.md) 的相应附录；其中 10 张精选卡片供按需补背景。

## 快速路径:dirty workspace 心跳接力

1. 读取相关路径的状态和 diff，确认目标、已有改动及本轮授权范围。
2. 选择原任务中可推进的部分，实施修改并运行相关检查。检查通过后不因模板齐全度继续扩展任务。
3. 报告结果、验证和实际阻塞；需要交接时写清下一步。只有任务包含提交时才 stage/commit，并核对提交范围。

具体边界分别查 [未知改动](dirty-target-file-blocks-continuation.md)、[失败输出](failure-output-must-change-plan.md)、[路径级提交](path-scoped-commit-boundary.md)。它们是遇到相应情况时的参考，不是每次任务的前置阅读清单。

## 交付工程化线索

只有本轮涉及可下载或发布资产时才进入这些检查：页面跳转查 [稳定锚点](referenced-section-needs-stable-anchor.md)，打包查 [staging](package-staging-stays-outside-output-dir.md) 和 [归档契约](artifact-smoke-test-checks-contract.md)，已跟踪生成物查 [漂移](tracked-artifact-needs-drift-check.md)。按本次产物选择相关项。

## 阅读顺序

下表保留全部卡片的查找入口，可按问题检索；排列不表示执行顺序。新读者可从 [Agent 的组成](agent-model-tool-loop-boundaries.md) 和 [第一个研究助手](first-agent-research-assistant.md) 开始。

| 卡片 | 文件 |
|---|---|
| Agent 是模型、工具、循环和边界的组合 | [agent-model-tool-loop-boundaries.md](agent-model-tool-loop-boundaries.md) |
| 第一个 Agent 先做研究助手，不要一开始做全能助手 | [first-agent-research-assistant.md](first-agent-research-assistant.md) |
| 工具描述要写用途和输入，不要只写名字 | [tool-descriptions-use-case-input.md](tool-descriptions-use-case-input.md) |
| 工具结果必须可观察，不要只返回“成功” | [tool-result-must-be-observable.md](tool-result-must-be-observable.md) |
| 记忆用于延续上下文，不是事实唯一来源 | [memory-is-context-not-source-of-truth.md](memory-is-context-not-source-of-truth.md) |
| 上下文预算是一种资源，不要把所有历史都塞进提示 | [context-budget-is-a-resource.md](context-budget-is-a-resource.md) |
| 上下文工程是状态设计，不是把材料拼成长提示 | [context-engineering-is-state-design.md](context-engineering-is-state-design.md) |
| 反馈必须区分事实和推断，不要把感觉当结论 | [feedback-must-separate-facts-and-inferences.md](feedback-must-separate-facts-and-inferences.md) |
| 有效反馈才触发修订，不要被每个声音牵着走 | [validated-feedback-triggers-revision.md](validated-feedback-triggers-revision.md) |
| 反馈池要把信号留成可执行字段 | [feedback-pool-keeps-signals-actionable.md](feedback-pool-keeps-signals-actionable.md) |
| Agent 必须有迭代上限和失败出口 | [agent-iteration-limit-failure-exit.md](agent-iteration-limit-failure-exit.md) |
| 心跳工作流让长期任务不漂移 | [heartbeat-workflow-prevents-drift.md](heartbeat-workflow-prevents-drift.md) |
| 工作日志是可复用资产，不要写成心情流水账 | [work-log-is-reusable-asset.md](work-log-is-reusable-asset.md) |
| 启动快照先于规划，不要凭上一轮印象选任务 | [startup-snapshot-before-planning.md](startup-snapshot-before-planning.md) |
| 日切换需要新快照，不要继承昨天的授权 | [day-rollover-needs-fresh-snapshot.md](day-rollover-needs-fresh-snapshot.md) |
| Multi-repo status matrix before task selection | [multi-repo-status-matrix-before-task-selection.md](multi-repo-status-matrix-before-task-selection.md) |
| 生成产物启动分诊先于工作选择 | [generated-artifact-startup-triage.md](generated-artifact-startup-triage.md) |
| 目标文件已有改动时，先确认归属和授权范围 | [dirty-target-file-blocks-continuation.md](dirty-target-file-blocks-continuation.md) |
| 规划要选择工作，不要只复述状态 | [planning-selects-work-not-just-summary.md](planning-selects-work-not-just-summary.md) |
| 交接必须写下一步动作，不要只写状态 | [handoff-must-name-next-action.md](handoff-must-name-next-action.md) |
| 先写人类假设，再让 Agent 动手 | [human-hypothesis-before-agent.md](human-hypothesis-before-agent.md) |
| 静默成功需要反向测试 | [silent-success-needs-negative-test.md](silent-success-needs-negative-test.md) |
| Standalone runner discovers tests | [standalone-runner-discovers-tests.md](standalone-runner-discovers-tests.md) |
| 接力点是信号，不是义务 | [continuation-is-signal-not-obligation.md](continuation-is-signal-not-obligation.md) |
| 无人值守 Agent 要选择默认动作，不要等待澄清 | [unattended-agent-chooses-default-action.md](unattended-agent-chooses-default-action.md) |
| 未提交接力文件先判断归属，不要直接接管 | [uncommitted-handoff-needs-ownership-triage.md](uncommitted-handoff-needs-ownership-triage.md) |
| Staged 改动不等于本轮所有权 | [staged-changes-are-not-ownership.md](staged-changes-are-not-ownership.md) |
| Path-scoped commit boundary prevents inherited dirty mix | [path-scoped-commit-boundary.md](path-scoped-commit-boundary.md) |
| 提交范围台账防止混入未知归属 | [commit-scope-ledger-prevents-mixed-ownership.md](commit-scope-ledger-prevents-mixed-ownership.md) |
| 多会话控制台先建台账，不要让 Agent 会话互相抢方向 | [multi-session-control-plane-needs-ledger.md](multi-session-control-plane-needs-ledger.md) |
| 其他 Agent Summary 边界先于提交范围 | [foreign-agent-summary-boundary.md](foreign-agent-summary-boundary.md) |
| Appendix template changes need neighbor sync | [appendix-template-changes-need-neighbor-sync.md](appendix-template-changes-need-neighbor-sync.md) |
| 双向导航闭合发布资产，不要只从 README 单向指路 | [bidirectional-navigation-closes-release-assets.md](bidirectional-navigation-closes-release-assets.md) |
| 阻断原因先做索引，不要继续扩模板 | [block-reason-index-precedes-template-sprawl.md](block-reason-index-precedes-template-sprawl.md) |
| Pre-task checklist is not retro asset log | [pre-task-checklist-is-not-retro-asset-log.md](pre-task-checklist-is-not-retro-asset-log.md) |
| 短节拍任务不要变成重构 | [short-cadence-tasks-must-not-become-refactors.md](short-cadence-tasks-must-not-become-refactors.md) |
| 交付预算防止心跳漂移，不要把节拍用成工具维护循环 | [delivery-budget-prevents-heartbeat-drift.md](delivery-budget-prevents-heartbeat-drift.md) |
| 新表面要有复用证明，不要把同一经验连续扩成近重复资产 | [no-new-surface-without-reuse-proof.md](no-new-surface-without-reuse-proof.md) |
| 项目切片先闭环，再提取可复用资产 | [project-slice-precedes-asset-extraction.md](project-slice-precedes-asset-extraction.md) |
| 样本入口不是待办队列，不要按文件名机械补齐 | [sample-entry-is-not-todo-queue.md](sample-entry-is-not-todo-queue.md) |
| 先确认 Green Baseline，再切换资产任务 | [green-baseline-before-asset-switch.md](green-baseline-before-asset-switch.md) |
| 安全债先分生产风险，不要默认 `audit fix --force` | [security-debt-prioritizes-production-before-force.md](security-debt-prioritizes-production-before-force.md) |
| 验证先于乐观总结，不要把“看起来完成”当完成 | [verify-before-optimistic-summary.md](verify-before-optimistic-summary.md) |
| 测试 Fixture 失败消息也是交接材料 | [test-fixture-failure-message-is-handoff.md](test-fixture-failure-message-is-handoff.md) |
| 解析层测试梯先于 Protected Mock | [parser-layer-test-ladder-before-protected-mocks.md](parser-layer-test-ladder-before-protected-mocks.md) |
| 薄 API 测试先锁控制流，不重复 200 | [thin-api-tests-target-control-flow-not-200.md](thin-api-tests-target-control-flow-not-200.md) |
| 未验证项要显式交接，不要藏在顺利总结里 | [unverified-items-need-explicit-handoff.md](unverified-items-need-explicit-handoff.md) |
| 本地 proof checker 先于重型构建，不要把每次小改都交给全量 build | [local-proof-checker-precedes-heavy-build.md](local-proof-checker-precedes-heavy-build.md) |
| DOM 测试环境前先锁 Helper 契约，不要为一个窄副作用扩大依赖面 | [helper-contract-before-dom-harness.md](helper-contract-before-dom-harness.md) |
| 双角色 E2E Helper 固定入口与权限契约 | [dual-role-e2e-helper-contract.md](dual-role-e2e-helper-contract.md) |
| 规格抽屉 E2E 要锁决策字段 | [spec-drawer-e2e-acceptance-contract.md](spec-drawer-e2e-acceptance-contract.md) |
| 依赖变更审批先共享测试表，不要让前后端规则各自漂移 | [dependency-mutation-approval-table.md](dependency-mutation-approval-table.md) |
| 全量 proof 基线先变绿，再把它写进常规 preflight | [full-proof-baseline-before-ci.md](full-proof-baseline-before-ci.md) |
| 统一 preflight wrapper 防止命令漂移，不要靠记忆拼验证清单 | [unified-preflight-wrapper-prevents-command-drift.md](unified-preflight-wrapper-prevents-command-drift.md) |
| 验证副作用要隔离，不要让 proof 命令顺手改出提交内容 | [verification-side-effects-need-quarantine.md](verification-side-effects-need-quarantine.md) |
| Proof output must be portable | [proof-output-must-be-portable.md](proof-output-must-be-portable.md) |
| 证据字段交接要写清生产者和消费者，不要让发布报告各说各话 | [evidence-field-handoff-prevents-release-drift.md](evidence-field-handoff-prevents-release-drift.md) |
| 最终报告要来自已提交状态，不要来自计划中的状态 | [report-from-committed-state.md](report-from-committed-state.md) |
| 最终报告要写清排除边界，不要只报完成项 | [final-report-names-excluded-boundaries.md](final-report-names-excluded-boundaries.md) |
| Dirty workspace 收尾要有清单，不要靠最后一眼状态 | [dirty-workspace-exit-checklist.md](dirty-workspace-exit-checklist.md) |
| 失败输出要改变计划，不要当作背景噪音 | [failure-output-must-change-plan.md](failure-output-must-change-plan.md) |
| Expected Failure 也是交付物 | [expected-failure-is-deliverable.md](expected-failure-is-deliverable.md) |
| AI 编程审查要先做固定范围 offer，不要一上来卖全栈自动化 | [ai-coding-audit-is-fixed-scope-offer.md](ai-coding-audit-is-fixed-scope-offer.md) |
| 试点报价卡把兴趣变成交易，不要把“愿意试试”当付费信号 | [pilot-offer-card-turns-interest-into-transaction.md](pilot-offer-card-turns-interest-into-transaction.md) |
| 证据请求不是完整审查，不要把取证当交付 | [evidence-request-is-not-full-audit.md](evidence-request-is-not-full-audit.md) |
| 先交付首份报告，不要先卖咨询 | [first-report-before-consulting.md](first-report-before-consulting.md) |
| 先跑 30 分钟路线，不要先产品化 | [thirty-minute-route-before-productizing.md](thirty-minute-route-before-productizing.md) |
| 外部发布先要授权，不要把草稿当成发布许可 | [external-publish-needs-authorization.md](external-publish-needs-authorization.md) |
| 发布闸门先字段化，不要让 `--push` 读取散文结论 | [publish-gate-fields-before-push.md](publish-gate-fields-before-push.md) |
| 已部署不等于公开 GO，不要把 production 状态写成发布许可 | [deployed-is-not-public-go.md](deployed-is-not-public-go.md) |
| 无真实链接时先验证需求，不要伪造发布入口 | [no-link-validation-before-launch.md](no-link-validation-before-launch.md) |
| Authorization blocker switches to proof work | [authorization-blocker-switches-to-proof-work.md](authorization-blocker-switches-to-proof-work.md) |
| 真实样例先于模板扩张，不要在无外部证据时继续堆产品表面 | [external-evidence-before-template-expansion.md](external-evidence-before-template-expansion.md) |
| 发布反馈先看证据形状，不要只看互动量 | [publish-feedback-needs-evidence-shape.md](publish-feedback-needs-evidence-shape.md) |
| AI 生成 PR 需要单独审查入口，不要混进普通代码审查 | [ai-generated-pr-needs-review-entry.md](ai-generated-pr-needs-review-entry.md) |
| AI 辅助 PR 审查路径要像产品阶梯，不要只是一组文章 | [ai-assisted-pr-review-path-is-product-ladder.md](ai-assisted-pr-review-path-is-product-ladder.md) |
| 先复用已有技能，不要把每条观察都写成新技能 | [reuse-existing-skill-before-new-skill.md](reuse-existing-skill-before-new-skill.md) |
| 下一条安全命令梯不是测试清单，不要只写“再跑一遍” | [next-safe-command-ladder-is-not-test-list.md](next-safe-command-ladder-is-not-test-list.md) |
| 匿名案例不能编造证据，不要把样板写成战报 | [anonymous-case-must-not-invent-evidence.md](anonymous-case-must-not-invent-evidence.md) |
| 公开案例先分事实、推断和未验证，不要把审查记录直接写成结论 | [public-case-separates-facts-inferences-unverified.md](public-case-separates-facts-inferences-unverified.md) |
| 模板入口先分两层，不要让 Agent 复制错输入 | [two-layer-template-entry-prevents-wrong-copy.md](two-layer-template-entry-prevents-wrong-copy.md) |
| Repo 里的 Agent 规则要有可见入口，不要只藏在聊天记录里 | [repo-agent-rules-need-visible-entry.md](repo-agent-rules-need-visible-entry.md) |
| Skill Metadata 是执行入口，不是装饰字段 | [skill-metadata-is-execution-surface.md](skill-metadata-is-execution-surface.md) |
| 被引用的页面区域需要稳定锚点，不要只在文案里说“上方/下方” | [referenced-section-needs-stable-anchor.md](referenced-section-needs-stable-anchor.md) |
| Package staging stays outside output dir | [package-staging-stays-outside-output-dir.md](package-staging-stays-outside-output-dir.md) |
| Artifact smoke test checks contract, not just existence | [artifact-smoke-test-checks-contract.md](artifact-smoke-test-checks-contract.md) |
| Tracked artifact needs drift check, not just regeneration | [tracked-artifact-needs-drift-check.md](tracked-artifact-needs-drift-check.md) |
| Shared package assertions prevent contract drift | [shared-package-assertions-prevent-contract-drift.md](shared-package-assertions-prevent-contract-drift.md) |
| AI 助手操作系统先分清身份、用户、工具和心跳 | [assistant-os-layers.md](assistant-os-layers.md) |
| 启动层只负责初始化，不应该长期参与运行 | [bootstrap-is-initialization-only.md](bootstrap-is-initialization-only.md) |
| Large dirty diff needs intake receipt | [large-dirty-diff-needs-intake-receipt.md](large-dirty-diff-needs-intake-receipt.md) |
| 格式 churn 先剥离，不要把语义改动埋进全章重排 | [format-churn-needs-semantic-split.md](format-churn-needs-semantic-split.md) |

## 维护与验证

新增卡片同步目录与计数。文案修改审读相应段落；索引、样本或链接变更运行 `python3 scripts/verify_tech_cards.py --full-only`，并复核卡片的“问题、要点、示例、坑、检查”五段。AI Agent 工作流卡片不属于语言代码 verifier 的覆盖范围。检查程序本身变更时再跑对应回归测试。
