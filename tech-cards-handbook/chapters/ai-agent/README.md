# AI Agent 系统实践卡片

本目录按"一张卡片一个 Markdown 文件"维护，共 87 张。文件名使用英文 `kebab-case`。

本目录收录 Agent 系统设计、运行边界、工具、记忆、反馈判断、反馈池和心跳工作流等实践卡片;具体 SDK 或语言实现优先放入对应技术栈目录。

本章不纳入 `scripts/verify_all_cards.py --language ...` 的语言代码 verifier;维护时以 `chapters/README.md` 的索引校验和链接校验为准,并人工复核每张卡片是否仍包含问题、要点、示例、坑、检查五段。

如果读者正在处理"周期性唤醒的 Agent + 已有 dirty workspace + 多 repo 接力"这类场景,优先使用 [`../../samples/ai-agent-dirty-workspace-one-pager.md`](../../samples/ai-agent-dirty-workspace-one-pager.md),再按下面的运行控制顺序深入阅读。

## 本章四条主线

本章 87 张卡片帮助 AI 时代的程序员用 agent 工作流提升验证力，围绕四条主线展开：

| 主线 | 解决的问题 | 入口 |
|---|---|---|
| 运行控制 | 心跳唤醒的 agent 如何在 dirty workspace 和日切换边界里不漂移、不混入未知改动 | 下面的「3 分钟读法」和「快速路径」 |
| 验证与证据 | 每轮交付如何有可复制、可移植的验证证据；阶段性红灯和窄副作用契约如何先被写成可复判证据，而不是模糊失败或乐观完成 | 阅读顺序第 3 节，验证系列卡片 |
| 所有权与交付 | commit 边界、交付物 smoke test 和发布授权如何清晰可审 | 阅读顺序第 3 节，所有权与交付系列卡片 |
| 产品化阶梯 | 如何把验证能力转化为可售的报告、案例和发布资产 | 阅读顺序第 3 节，AI 编程审查系列卡片 |

如果时间有限，先从「3 分钟读法」的三条线入手；如果需要完整背景，按「阅读顺序」的四个阶段循序读。

## 3 分钟读法

如果只想马上减少一次心跳接力的事故率,先按三条线读,不要从全部卡片顺序扫完:

1. **失败吸收线**:读 [`failure-output-must-change-plan.md`](failure-output-must-change-plan.md),再用 [`../../samples/ai-agent-failure-absorption-one-pager.md`](../../samples/ai-agent-failure-absorption-one-pager.md) 记录`信号 -> 影响 -> 证据位置`,确认失败是否改变了范围、顺序、目标或交接。
2. **dirty workspace 线**:读 [`startup-snapshot-before-planning.md`](startup-snapshot-before-planning.md)、[`day-rollover-needs-fresh-snapshot.md`](day-rollover-needs-fresh-snapshot.md)、[`multi-repo-status-matrix-before-task-selection.md`](multi-repo-status-matrix-before-task-selection.md)、[`human-hypothesis-before-agent.md`](human-hypothesis-before-agent.md)、[`silent-success-needs-negative-test.md`](silent-success-needs-negative-test.md)、[`uncommitted-handoff-needs-ownership-triage.md`](uncommitted-handoff-needs-ownership-triage.md)、[`staged-changes-are-not-ownership.md`](staged-changes-are-not-ownership.md)、[`path-scoped-commit-boundary.md`](path-scoped-commit-boundary.md)、[`multi-session-control-plane-needs-ledger.md`](multi-session-control-plane-needs-ledger.md) 和 [`large-dirty-diff-needs-intake-receipt.md`](large-dirty-diff-needs-intake-receipt.md),先分清启动前改动、日切换新快照、多 repo 状态矩阵、自己的可证伪假设、静默成功风险、staged path、路径级提交边界、多会话 owned paths、大 dirty diff 接收回执、可接管 path,再决定本轮文件范围。
3. **提交证据线**:读 [`commit-scope-ledger-prevents-mixed-ownership.md`](commit-scope-ledger-prevents-mixed-ownership.md)、[`verification-side-effects-need-quarantine.md`](verification-side-effects-need-quarantine.md)、[`dirty-workspace-exit-checklist.md`](dirty-workspace-exit-checklist.md)、[`report-from-committed-state.md`](report-from-committed-state.md) 和 [`evidence-field-handoff-prevents-release-drift.md`](evidence-field-handoff-prevents-release-drift.md),最终报告从已提交状态读回 hash,同时写清验证副作用和排除边界；如果本轮是文档/索引/配置小改，先用 [`../../samples/ai-agent-proof-checker-one-pager.md`](../../samples/ai-agent-proof-checker-one-pager.md) 设计轻量 preflight，再用 [`../../samples/ai-agent-next-safe-command-ladder-one-pager.md`](../../samples/ai-agent-next-safe-command-ladder-one-pager.md) 把验证清单改写为“当前最大风险 -> 下一条安全命令 -> pass/fail 语义”的命令梯；收尾前可用 [`../../samples/ai-agent-final-report-field-quickref.md`](../../samples/ai-agent-final-report-field-quickref.md) 核对固定字段。若跨阶段报告字段正在漂移，先用证据字段 handoff 卡确认字段生产者、补齐者和消费者，再复制 [`../../samples/ai-agent-evidence-field-handoff-one-pager.md`](../../samples/ai-agent-evidence-field-handoff-one-pager.md) 填字段表和检查片段；若验证失败或无法执行，用 [`../../samples/ai-agent-verification-failure-handoff-template.md`](../../samples/ai-agent-verification-failure-handoff-template.md) 交接失败证据；若只是存在未覆盖边界，用 [`../../samples/ai-agent-unverified-handoff-one-pager.md`](../../samples/ai-agent-unverified-handoff-one-pager.md) 把已验证事实、未验证项、结论措辞和下一步第一条动作拆开。


完成这三条线后,再进入下面的 26 步快速路径补齐运行控制细节；如果要把整套输入直接交给下一轮 Agent，使用 [`../../samples/ai-agent-sample-pack.md`](../../samples/ai-agent-sample-pack.md) 中的 10 张精选卡片、附录和配套一页纸模板。验证类输入按两层入口选择：样本包开头的“验证入口速记”适合 30 秒内按“当前最大风险”做入口判断，决定该接 proof checker、全量基线、preflight wrapper、命令梯还是交接模板；如果不确定该复制哪份输入，先看 [`../../samples/README.md`](../../samples/README.md) 的场景索引。若困惑集中在 proof checker、全量基线、preflight wrapper 和命令梯的先后顺序，再用 [`../../samples/ai-agent-proof-to-preflight-decision-table.md`](../../samples/ai-agent-proof-to-preflight-decision-table.md) 做 2 分钟展开判断。

## 快速路径:dirty workspace 心跳接力

这条路径不是通用入门顺序,而是给已经在真实项目里工作的 Agent 使用:先建立启动快照,把上一轮接力点当作信号而不是义务,再选择可安全推进的小任务,最后把成果和未接管边界同时写清。它和样本包的关系是：本表负责解释为什么按 26 步推进，样本包负责提供可复制 prompt、证据表和最终报告字段。

| 步骤 | 阶段 | 目标 | 卡片 |
|---|---|---|---|
| 1 | 唤醒与事实 | 防止凭上一轮印象行动 | [`heartbeat-workflow-prevents-drift.md`](heartbeat-workflow-prevents-drift.md) |
| 2 | 唤醒与事实 | 把工作日志写成下一轮可复用资产 | [`work-log-is-reusable-asset.md`](work-log-is-reusable-asset.md) |
| 3 | 唤醒与事实 | 在规划前保存当前 repo 状态 | [`startup-snapshot-before-planning.md`](startup-snapshot-before-planning.md) |
| 3a | 唤醒与事实 | 跨零点后重开今天 notebook 并重跑 repo 快照 | [`day-rollover-needs-fresh-snapshot.md`](day-rollover-needs-fresh-snapshot.md) |
| 3b | 唤醒与事实 | 多 repo 先分 clean / owned-dirty / unknown-dirty / summary-only，再选任务 | [`multi-repo-status-matrix-before-task-selection.md`](multi-repo-status-matrix-before-task-selection.md) |
| 4 | 规划与取舍 | 从候选工作中做取舍 | [`planning-selects-work-not-just-summary.md`](planning-selects-work-not-just-summary.md) |
| 5 | 规划与取舍 | 把上一轮接力点当作信号,而不是自动义务 | [`continuation-is-signal-not-obligation.md`](continuation-is-signal-not-obligation.md) |
| 6 | 规划与取舍 | 先写可证伪的人类假设,再让 Agent 生成或修改 | [`human-hypothesis-before-agent.md`](human-hypothesis-before-agent.md) |
| 7 | 规划与取舍 | 无人值守时选择低风险默认动作,而不是等待澄清 | [`unattended-agent-chooses-default-action.md`](unattended-agent-chooses-default-action.md) |
| 8 | 发布与授权 | 外部发布必须先拿到渠道、账号、联系路径和观察窗口授权 | [`external-publish-needs-authorization.md`](external-publish-needs-authorization.md) |
| 8a | 发布与授权 | 发布闸门先字段化，不让 `--push` 从散文结论里猜授权 | [`publish-gate-fields-before-push.md`](publish-gate-fields-before-push.md) |
| 9 | 发布与授权 | 无真实支付/留资/试读链接时先验证需求原话，不伪造发布入口 | [`no-link-validation-before-launch.md`](no-link-validation-before-launch.md) |
| 10 | 验证与失败语义 | 防止无效输入或空检查集合被误报为成功 | [`silent-success-needs-negative-test.md`](silent-success-needs-negative-test.md) |
| 10a | 验证与失败语义 | 防止 standalone 测试入口因手写清单漏项而静默成功 | [`standalone-runner-discovers-tests.md`](standalone-runner-discovers-tests.md) |
| 11 | 规划与取舍 | 让失败输出改变范围、顺序、目标或交接 | [`failure-output-must-change-plan.md`](failure-output-must-change-plan.md) |
| 12 | 所有权边界 | 对启动前 dirty 接力文件做归属判断;最终报告保留状态证据 | [`uncommitted-handoff-needs-ownership-triage.md`](uncommitted-handoff-needs-ownership-triage.md) |
| 13 | 所有权边界 | 单独识别启动前 staged path,不把 index 状态误当授权;状态证据必须进入最终报告 | [`staged-changes-are-not-ownership.md`](staged-changes-are-not-ownership.md) |
| 14 | 所有权边界 | 用提交范围台账防止混入未知归属;台账包含状态证据列 | [`commit-scope-ledger-prevents-mixed-ownership.md`](commit-scope-ledger-prevents-mixed-ownership.md) |
| 14a | 所有权边界 | 多会话并行前先登记 Session / Permission / Evidence / Handoff 台账 | [`multi-session-control-plane-needs-ledger.md`](multi-session-control-plane-needs-ledger.md) |
| 15 | 所有权边界 | 大 dirty diff 先写接收回执,不要把局部小修混进未知归属的大改写 | [`large-dirty-diff-needs-intake-receipt.md`](large-dirty-diff-needs-intake-receipt.md) |
| 15a | 所有权边界 | 格式 churn 先剥离,不要把语义改动埋进全章重排 | [`format-churn-needs-semantic-split.md`](format-churn-needs-semantic-split.md) |
| 15b | 所有权边界 | 附录模板增强先对齐邻近模板,不要让权限、证据和回退字段只出现在一个入口 | [`appendix-template-changes-need-neighbor-sync.md`](appendix-template-changes-need-neighbor-sync.md) |
| 15c | 所有权边界 | 发布资产要双向导航闭合,不要只从 README 单向指路 | [`bidirectional-navigation-closes-release-assets.md`](bidirectional-navigation-closes-release-assets.md) |
| 15d | 所有权边界 | 阻断原因先做索引,不要继续扩模板 | [`block-reason-index-precedes-template-sprawl.md`](block-reason-index-precedes-template-sprawl.md) |
| 15e | 所有权边界 | 任务前清单和复盘沉淀卡先分生命周期,不要为了字段整齐混成一张表 | [`pre-task-checklist-is-not-retro-asset-log.md`](pre-task-checklist-is-not-retro-asset-log.md) |
| 15f | 所有权边界 | 在 dirty repo 里只 stage 本轮 owned paths,不要把启动前 dirty path 混进提交 | [`path-scoped-commit-boundary.md`](path-scoped-commit-boundary.md) |
| 16 | 范围与预算 | 给心跳交付设预算,避免连续工具维护循环 | [`delivery-budget-prevents-heartbeat-drift.md`](delivery-budget-prevents-heartbeat-drift.md) |
| 17 | 范围与预算 | 第三个同主题表面必须先证明下一轮会复用 | [`no-new-surface-without-reuse-proof.md`](no-new-surface-without-reuse-proof.md) |
| 17a | 范围与预算 | 项目切片先闭环，再提取 docs/skill/book 资产 | [`project-slice-precedes-asset-extraction.md`](project-slice-precedes-asset-extraction.md) |
| 18 | 范围与预算 | 样本入口只做风险选择，不要按文件名机械补齐 | [`sample-entry-is-not-todo-queue.md`](sample-entry-is-not-todo-queue.md) |
| 19 | 范围与预算 | 工程红灯修完后先确认 green baseline，再切换到资产任务 | [`green-baseline-before-asset-switch.md`](green-baseline-before-asset-switch.md) |
| 20 | 收尾与状态证据 | 用清单做 path-limited 收尾 | [`dirty-workspace-exit-checklist.md`](dirty-workspace-exit-checklist.md) |
| 21 | 收尾与状态证据 | 先跑聚焦验证并显式交接未验证项 | [`verify-before-optimistic-summary.md`](verify-before-optimistic-summary.md)、[`unverified-items-need-explicit-handoff.md`](unverified-items-need-explicit-handoff.md); 命令梯模板见 [`../../samples/ai-agent-next-safe-command-ladder-one-pager.md`](../../samples/ai-agent-next-safe-command-ladder-one-pager.md)，未验证项一页纸见 [`../../samples/ai-agent-unverified-handoff-one-pager.md`](../../samples/ai-agent-unverified-handoff-one-pager.md) |
| 21a | 验证与失败语义 | 把阶段性红灯写成可复判契约，防止下一轮为追绿误改 gate | [`expected-failure-is-deliverable.md`](expected-failure-is-deliverable.md) |
| 21b | 验证与失败语义 | 把测试 fixture panic 写成下一轮能定位阶段的交接材料 | [`test-fixture-failure-message-is-handoff.md`](test-fixture-failure-message-is-handoff.md) |
| 21c | 验证与失败语义 | 进入 protected parser/mock 前先按链路层级选择更低 mock 的测试边界 | [`parser-layer-test-ladder-before-protected-mocks.md`](parser-layer-test-ladder-before-protected-mocks.md) |
| 21d | 验证与失败语义 | 薄 API 单测先锁短路、校验、错误转发和参数转换，不重复 integration 已覆盖的 200 | [`thin-api-tests-target-control-flow-not-200.md`](thin-api-tests-target-control-flow-not-200.md) |
| 22 | 验证与集成边界 | 先用窄范围 proof checker 或 helper 契约证明基础契约,再把渲染和插件行为交给重型构建；若同一真实入口要覆盖多角色和多 viewport，先把动作 helper 与断言 helper 分开；若规格抽屉承担素材、平台和缺口交接，先锁决策字段而不是只测容器打开；若执行命令会改变依赖或环境，先共享测试表再分别改前端预扫描、后端执行策略和确认文案；若要升级为常规必跑项，先建立全量红绿基线，再把稳定命令收束成统一 preflight wrapper；验证命令写出 generated diff 时先隔离副作用 | [`local-proof-checker-precedes-heavy-build.md`](local-proof-checker-precedes-heavy-build.md)、[`helper-contract-before-dom-harness.md`](helper-contract-before-dom-harness.md)、[`dual-role-e2e-helper-contract.md`](dual-role-e2e-helper-contract.md)、[`spec-drawer-e2e-acceptance-contract.md`](spec-drawer-e2e-acceptance-contract.md)、[`dependency-mutation-approval-table.md`](dependency-mutation-approval-table.md)、[`full-proof-baseline-before-ci.md`](full-proof-baseline-before-ci.md)、[`unified-preflight-wrapper-prevents-command-drift.md`](unified-preflight-wrapper-prevents-command-drift.md)、[`verification-side-effects-need-quarantine.md`](verification-side-effects-need-quarantine.md); 可复制输入见 [`../../samples/ai-agent-proof-to-preflight-decision-table.md`](../../samples/ai-agent-proof-to-preflight-decision-table.md)、[`../../samples/ai-agent-proof-checker-one-pager.md`](../../samples/ai-agent-proof-checker-one-pager.md)、[`../../samples/ai-agent-full-proof-baseline-one-pager.md`](../../samples/ai-agent-full-proof-baseline-one-pager.md)、[`../../samples/ai-agent-preflight-wrapper-one-pager.md`](../../samples/ai-agent-preflight-wrapper-one-pager.md) |
| 23 | 证据可移植性 | 让验证输出可复制到 notebook 和最终报告 | [`proof-output-must-be-portable.md`](proof-output-must-be-portable.md) |
| 24 | 报告与读回 | 从已提交状态读回 hash 和 subject;报告包含启动/收尾状态证据 | [`report-from-committed-state.md`](report-from-committed-state.md) |
| 25 | 报告与读回 | 最终响应同时列成果和排除项 | [`final-report-names-excluded-boundaries.md`](final-report-names-excluded-boundaries.md) |

失败吸收线索：步骤 11 不是事后解释失败，而是要求失败输出立刻改变范围、顺序、目标或交接；可先读 [`failure-output-must-change-plan.md`](failure-output-must-change-plan.md)，再用 [`../../samples/ai-agent-failure-absorption-one-pager.md`](../../samples/ai-agent-failure-absorption-one-pager.md) 做收尾检查，并对照 [`../../samples/ai-agent-sample-pack.md`](../../samples/ai-agent-sample-pack.md) 中“失败吸收速记”的四类最小改计划例子，检查最终 notebook 是否写清“失败如何改变了本轮选择”。

状态证据线索：步骤 12–15 的卡片要求最终报告保留启动/收尾 `git status --short`、分 repo 读回 commit hash、提交范围台账和大 dirty diff 接收回执；读者可按这条线索从所有权边界串到最终报告，并用 [`../../samples/ai-agent-sample-pack.md`](../../samples/ai-agent-sample-pack.md) 的样本包、[`../../samples/ai-agent-dirty-workspace-one-pager.md`](../../samples/ai-agent-dirty-workspace-one-pager.md) 的一页纸和 [`../../samples/ai-agent-final-report-field-quickref.md`](../../samples/ai-agent-final-report-field-quickref.md) 的字段速查核对可复制输入是否同步。

交付工程化线索：当 Agent 的本轮成果是 zip、静态页、清单或可下载模板这类可交付资产时，不要只按 dirty workspace 路径收尾。先用 [`referenced-section-needs-stable-anchor.md`](referenced-section-needs-stable-anchor.md) 检查页面文案引用的区域是否有稳定锚点；再用 [`package-staging-stays-outside-output-dir.md`](package-staging-stays-outside-output-dir.md) 确认打包 staging 不污染 `--out-dir`；接着用 [`artifact-smoke-test-checks-contract.md`](artifact-smoke-test-checks-contract.md) 把 smoke test 从“文件存在”升级为“归档根目录、关键入口、禁止文件、无残留”契约；最后用 [`tracked-artifact-needs-drift-check.md`](tracked-artifact-needs-drift-check.md) 区分临时目录验证和 tracked artifact 漂移检查。若同类检查已经在多个 package smoke test 中重复出现，再读 [`shared-package-assertions-prevent-contract-drift.md`](shared-package-assertions-prevent-contract-drift.md)，只把输出目录卫生、portable output 和 tracked/fresh 对比这类通用契约抽成共享 helper。这个顺序适合把一次可售资料包修复，压缩成下一轮可以直接复制的发布前检查路径。

配套可复制输入见 [`../../samples/ai-agent-sample-pack.md`](../../samples/ai-agent-sample-pack.md) 的 dirty workspace 心跳交接样例；若只需要收尾核对，先读 [`../../samples/ai-agent-dirty-workspace-one-pager.md`](../../samples/ai-agent-dirty-workspace-one-pager.md) 和 [`dirty-workspace-exit-checklist.md`](dirty-workspace-exit-checklist.md)，再按"验证证据 -> 状态证据 -> 已提交状态读回 -> 排除边界"的顺序把启动/收尾 `git status --short` 摘要和 [`final-report-names-excluded-boundaries.md`](final-report-names-excluded-boundaries.md) 的最终响应模板填完整。若本轮需要在轻量 proof、全量基线、preflight wrapper、命令梯和失败交接之间选入口，先用 [`../../samples/ai-agent-proof-to-preflight-decision-table.md`](../../samples/ai-agent-proof-to-preflight-decision-table.md) 做判断；若需要解释轻量验证和重型构建的分工，复制 [`../../samples/ai-agent-proof-checker-one-pager.md`](../../samples/ai-agent-proof-checker-one-pager.md) 的风险表与 notebook 句式；若要把 proof checker 升级成 AGENTS/preflight/CI 候选，再用 [`../../samples/ai-agent-full-proof-baseline-one-pager.md`](../../samples/ai-agent-full-proof-baseline-one-pager.md) 记录全量红绿基线、失败分类和升级判断；若全量基线已绿且验证命令开始分散，用 [`../../samples/ai-agent-preflight-wrapper-one-pager.md`](../../samples/ai-agent-preflight-wrapper-one-pager.md) 判断是否收束成统一 wrapper，并写清默认模式、快速模式、失败标签和编排测试；若本轮只是写了“lint/test/build”清单，先用 [`../../samples/ai-agent-next-safe-command-ladder-one-pager.md`](../../samples/ai-agent-next-safe-command-ladder-one-pager.md) 补齐当前最大风险、每级 pass/fail 语义和停止条件；若最终仍有未覆盖边界，用 [`../../samples/ai-agent-unverified-handoff-one-pager.md`](../../samples/ai-agent-unverified-handoff-one-pager.md) 写清已验证事实、未验证原因、结论边界和下一段第一条动作。

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
| 工作日志是可复用资产，不要写成心情流水账 | [`work-log-is-reusable-asset.md`](work-log-is-reusable-asset.md) |
| 启动快照先于规划,不要凭上一轮印象选任务 | [`startup-snapshot-before-planning.md`](startup-snapshot-before-planning.md) |
| 日切换需要新快照，不要继承昨天的授权 | [`day-rollover-needs-fresh-snapshot.md`](day-rollover-needs-fresh-snapshot.md) |
| 多 repo 状态矩阵先于任务选择,不要把 unknown dirty 或 summary-only 当默认工作 | [`multi-repo-status-matrix-before-task-selection.md`](multi-repo-status-matrix-before-task-selection.md) |
| 规划要选择工作,不要只复述状态 | [`planning-selects-work-not-just-summary.md`](planning-selects-work-not-just-summary.md) |
| 交接必须写下一步动作,不要只写状态 | [`handoff-must-name-next-action.md`](handoff-must-name-next-action.md) |
| 先写人类假设，再让 Agent 动手 | [`human-hypothesis-before-agent.md`](human-hypothesis-before-agent.md) |
| 静默成功需要反向测试，不要把空检查集合当 proof | [`silent-success-needs-negative-test.md`](silent-success-needs-negative-test.md) |
| Standalone runner 要自动发现测试，不要维护会漏项的手写清单 | [`standalone-runner-discovers-tests.md`](standalone-runner-discovers-tests.md) |
| 接力点是信号,不是义务 | [`continuation-is-signal-not-obligation.md`](continuation-is-signal-not-obligation.md) |
| 无人值守 Agent 要选择默认动作,不要等待澄清 | [`unattended-agent-chooses-default-action.md`](unattended-agent-chooses-default-action.md) |
| 未提交接力文件先判断归属,不要直接接管 | [`uncommitted-handoff-needs-ownership-triage.md`](uncommitted-handoff-needs-ownership-triage.md) |
| Staged 改动不等于本轮所有权 | [`staged-changes-are-not-ownership.md`](staged-changes-are-not-ownership.md) |
| 路径级提交边界防止混入继承 dirty | [`path-scoped-commit-boundary.md`](path-scoped-commit-boundary.md) |
| 提交范围台账防止混入未知归属 | [`commit-scope-ledger-prevents-mixed-ownership.md`](commit-scope-ledger-prevents-mixed-ownership.md) |
| 多会话控制台先建台账，不要让 Agent 会话互相抢方向 | [`multi-session-control-plane-needs-ledger.md`](multi-session-control-plane-needs-ledger.md) |
| 附录模板增强需要同步相邻模板，不要只改一个入口 | [`appendix-template-changes-need-neighbor-sync.md`](appendix-template-changes-need-neighbor-sync.md) |
| 双向导航闭合发布资产，不要只从 README 单向指路 | [`bidirectional-navigation-closes-release-assets.md`](bidirectional-navigation-closes-release-assets.md) |
| 阻断原因先做索引，不要继续扩模板 | [`block-reason-index-precedes-template-sprawl.md`](block-reason-index-precedes-template-sprawl.md) |
| 任务前清单不是复盘资产日志，不要为了字段整齐混淆生命周期 | [`pre-task-checklist-is-not-retro-asset-log.md`](pre-task-checklist-is-not-retro-asset-log.md) |
| 短节拍任务不要变成重构 | [`short-cadence-tasks-must-not-become-refactors.md`](short-cadence-tasks-must-not-become-refactors.md) |
| 交付预算防止心跳漂移 | [`delivery-budget-prevents-heartbeat-drift.md`](delivery-budget-prevents-heartbeat-drift.md) |
| 新表面要有复用证明 | [`no-new-surface-without-reuse-proof.md`](no-new-surface-without-reuse-proof.md) |
| 项目切片先闭环，再提取可复用资产 | [`project-slice-precedes-asset-extraction.md`](project-slice-precedes-asset-extraction.md) |
| 样本入口不是待办队列 | [`sample-entry-is-not-todo-queue.md`](sample-entry-is-not-todo-queue.md) |
| 先确认 Green Baseline，再切换资产任务 | [`green-baseline-before-asset-switch.md`](green-baseline-before-asset-switch.md) |
| 安全债先分生产风险，不要默认 `audit fix --force` | [`security-debt-prioritizes-production-before-force.md`](security-debt-prioritizes-production-before-force.md) |
| 验证先于乐观总结,不要把"看起来完成"当完成 | [`verify-before-optimistic-summary.md`](verify-before-optimistic-summary.md) |
| 测试 Fixture 失败消息也是交接材料 | [`test-fixture-failure-message-is-handoff.md`](test-fixture-failure-message-is-handoff.md) |
| 解析层测试梯先于 Protected Mock | [`parser-layer-test-ladder-before-protected-mocks.md`](parser-layer-test-ladder-before-protected-mocks.md) |
| 薄 API 测试先锁控制流，不重复 200 | [`thin-api-tests-target-control-flow-not-200.md`](thin-api-tests-target-control-flow-not-200.md) |
| 未验证项要显式交接,不要藏在顺利总结里 | [`unverified-items-need-explicit-handoff.md`](unverified-items-need-explicit-handoff.md) |
| 本地 proof checker 先于重型构建，不要把每次小改都交给全量 build | [`local-proof-checker-precedes-heavy-build.md`](local-proof-checker-precedes-heavy-build.md) |
| DOM 测试环境前先锁 Helper 契约，不要为一个窄副作用扩大依赖面 | [`helper-contract-before-dom-harness.md`](helper-contract-before-dom-harness.md) |
| 双角色 E2E Helper 固定入口与权限契约，不要让重复断言多点漂移 | [`dual-role-e2e-helper-contract.md`](dual-role-e2e-helper-contract.md) |
|| 规格抽屉 E2E 要锁决策字段，不要只测审查面板容器打开 | [`spec-drawer-e2e-acceptance-contract.md`](spec-drawer-e2e-acceptance-contract.md) |
|| 依赖变更审批先共享测试表，不要让前后端规则各自漂移 | [`dependency-mutation-approval-table.md`](dependency-mutation-approval-table.md) |
|| 全量 proof 基线先变绿，再把它写进常规 preflight | [`full-proof-baseline-before-ci.md`](full-proof-baseline-before-ci.md) |
| 统一 preflight wrapper 防止命令漂移，不要靠记忆拼验证清单 | [`unified-preflight-wrapper-prevents-command-drift.md`](unified-preflight-wrapper-prevents-command-drift.md) |
| 验证副作用要隔离，不要让 proof 命令顺手改出提交内容 | [`verification-side-effects-need-quarantine.md`](verification-side-effects-need-quarantine.md) |
| Proof 输出要可移植，不要把本机路径复制进交接证据 | [`proof-output-must-be-portable.md`](proof-output-must-be-portable.md) |
| 证据字段交接要写清生产者和消费者，不要让发布报告各说各话 | [`evidence-field-handoff-prevents-release-drift.md`](evidence-field-handoff-prevents-release-drift.md) |
| 最终报告要来自已提交状态,不要来自计划中的状态 | [`report-from-committed-state.md`](report-from-committed-state.md) |
| 最终报告要写清排除边界,不要只报完成项 | [`final-report-names-excluded-boundaries.md`](final-report-names-excluded-boundaries.md) |
| Dirty workspace 收尾要有清单,不要靠最后一眼状态 | [`dirty-workspace-exit-checklist.md`](dirty-workspace-exit-checklist.md) |
| 失败输出要改变计划,不要当作背景噪音 | [`failure-output-must-change-plan.md`](failure-output-must-change-plan.md) |
| Expected Failure 也是交付物 | [`expected-failure-is-deliverable.md`](expected-failure-is-deliverable.md) |
| AI 编程审查要先做固定范围 offer,不要一上来卖全栈自动化 | [`ai-coding-audit-is-fixed-scope-offer.md`](ai-coding-audit-is-fixed-scope-offer.md)；可复制交付物见 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md)，公开复盘前用 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) 降级证据不足的 claim |
| 试点报价卡把兴趣变成交易,不要把“愿意试试”当付费信号 | [`pilot-offer-card-turns-interest-into-transaction.md`](pilot-offer-card-turns-interest-into-transaction.md) |
| 证据请求不是完整审查，不要把取证当交付 | [`evidence-request-is-not-full-audit.md`](evidence-request-is-not-full-audit.md)；可发送话术见 `docs/documents/trending/ai/ai-coding-audit-evidence-request-template.md` |
| 先交付首份报告，不要先卖咨询 | [`first-report-before-consulting.md`](first-report-before-consulting.md)；报告骨架见 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md) |
| 先跑 30 分钟路线，不要先产品化 | [`thirty-minute-route-before-productizing.md`](thirty-minute-route-before-productizing.md)；路线收口可复用 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md) |
| 外部发布先要授权，不要把草稿当成发布许可 | [`external-publish-needs-authorization.md`](external-publish-needs-authorization.md)；可复制授权包见 [`../../samples/ai-agent-external-publish-authorization-one-pager.md`](../../samples/ai-agent-external-publish-authorization-one-pager.md) |
| 发布闸门先字段化，不要让 `--push` 读取散文结论 | [`publish-gate-fields-before-push.md`](publish-gate-fields-before-push.md) |
| 无真实链接时先验证需求，不要伪造发布入口 | [`no-link-validation-before-launch.md`](no-link-validation-before-launch.md) |
| 真实样例先于模板扩张，不要在无外部证据时继续堆产品表面 | [`external-evidence-before-template-expansion.md`](external-evidence-before-template-expansion.md) |
| 发布反馈先看证据形状，不要只看互动量 | [`publish-feedback-needs-evidence-shape.md`](publish-feedback-needs-evidence-shape.md)；从报告到案例的发布决策见 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) |
| AI 生成 PR 需要单独审查入口,不要混进普通代码审查 | [`ai-generated-pr-needs-review-entry.md`](ai-generated-pr-needs-review-entry.md) |
| AI 辅助 PR 审查路径要像产品阶梯,不要只是一组文章 | [`ai-assisted-pr-review-path-is-product-ladder.md`](ai-assisted-pr-review-path-is-product-ladder.md)；交付层接 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md)，公开复盘前接 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) |
| 先复用已有技能，不要把每条观察都写成新技能 | [`reuse-existing-skill-before-new-skill.md`](reuse-existing-skill-before-new-skill.md)；判断是否值得技能化前先填 [`../../samples/ai-agent-skill-reuse-before-new-skill-one-pager.md`](../../samples/ai-agent-skill-reuse-before-new-skill-one-pager.md) |
| 下一条安全命令梯不是测试清单，不要只写“再跑一遍” | [`next-safe-command-ladder-is-not-test-list.md`](next-safe-command-ladder-is-not-test-list.md) |
| 匿名案例不能编造证据，不要把样板写成战报 | [`anonymous-case-must-not-invent-evidence.md`](anonymous-case-must-not-invent-evidence.md)；发布前先用 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) 判断 Continue / Narrow / Stop |
| 公开案例先分事实、推断和未验证，不要把审查记录直接写成结论 | [`public-case-separates-facts-inferences-unverified.md`](public-case-separates-facts-inferences-unverified.md)；claim 标签模板见 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) |
| 模板入口先分两层，不要让 Agent 复制错输入 | [`two-layer-template-entry-prevents-wrong-copy.md`](two-layer-template-entry-prevents-wrong-copy.md) |
| Repo 里的 Agent 规则要有可见入口,不要只藏在聊天记录里 | [`repo-agent-rules-need-visible-entry.md`](repo-agent-rules-need-visible-entry.md) |
| Skill Metadata 是执行入口，不是装饰字段 | [`skill-metadata-is-execution-surface.md`](skill-metadata-is-execution-surface.md) |
| 被引用的页面区域需要稳定锚点，不要只在文案里说“上方/下方” | [`referenced-section-needs-stable-anchor.md`](referenced-section-needs-stable-anchor.md) |
| 打包 staging 要留在输出目录外，不要让交付命令污染 `--out-dir` | [`package-staging-stays-outside-output-dir.md`](package-staging-stays-outside-output-dir.md) |
| 交付物 smoke test 要检查契约，不要只检查文件存在 | [`artifact-smoke-test-checks-contract.md`](artifact-smoke-test-checks-contract.md) |
| 被追踪生成物需要漂移检查，不要只证明重新生成成功 | [`tracked-artifact-needs-drift-check.md`](tracked-artifact-needs-drift-check.md) |
| 共享 package 断言防止契约漂移，不要让每个打包测试复制不同口径 | [`shared-package-assertions-prevent-contract-drift.md`](shared-package-assertions-prevent-contract-drift.md) |

### 4. 最后抽象为助手操作系统

| 卡片 | 文件 |
|---|---|
| AI 助手操作系统先分清身份、用户、工具和心跳 | [`assistant-os-layers.md`](assistant-os-layers.md) |
| 启动层只负责初始化,不应该长期参与运行 | [`bootstrap-is-initialization-only.md`](bootstrap-is-initialization-only.md) |
