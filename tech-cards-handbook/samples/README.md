# Tech Cards Handbook Samples

本目录放可复制的 agent 输入、审查样例、一页纸模板和交接片段；它们不是正式卡片，不计入 `chapters/` 的卡片数。维护样本入口时，优先让读者能在 30 秒内回答：我该复制哪一份、它解决哪类接力风险、还需要回到哪张卡片补背景。

术语口径：本目录统一用“验证入口速记”指样本包顶部的 30 秒选择表，用“当前最大风险”作为选择第一列，用“入口判断”指在 proof checker、全量 proof 基线、统一 preflight wrapper、命令梯和交接模板之间只选下一份输入。

## 推荐入口

按当前场景选一份输入即可。表中其他模板只在出现相应问题时使用；已有项目规则和用户授权优先，样本不自动创建新任务或发布权限。

| 场景 | 先用 | 作用 |
|---|---|---|
| 完整 dirty workspace 接力：周期性唤醒的 Agent 面对 dirty workspace，需要完整 prompt、证据表和最终报告字段 | [`ai-agent-sample-pack.md`](ai-agent-sample-pack.md) | 10 张精选卡片建立最小闭环，附录和配套模板补足执行输入 |
| 只需要一页纸启动一次 dirty workspace 接力 | [`ai-agent-dirty-workspace-one-pager.md`](ai-agent-dirty-workspace-one-pager.md) | 压缩启动快照、归属判断、path-limited 推进和收尾报告 |
| 上一轮点名的目标文件在启动快照里已经 dirty，担心把接力点误当授权 | [`ai-agent-dirty-workspace-one-pager.md`](ai-agent-dirty-workspace-one-pager.md) 的“规划取舍”和 [`../chapters/ai-agent/dirty-target-file-blocks-continuation.md`](../chapters/ai-agent/dirty-target-file-blocks-continuation.md) | 先看 diff、归属和授权；明确且能保留已有改动时继续，只暂停冲突或未知部分，继续原任务内独立工作 |
| 共享 `summaries/` 里出现其他 agent notebook，担心 `git add .` 误提交或替对方整理 | [`ai-agent-sample-pack.md`](ai-agent-sample-pack.md) 的“验证入口速记”和卡片 8、9；提交前回到 [`../chapters/ai-agent/foreign-agent-summary-boundary.md`](../chapters/ai-agent/foreign-agent-summary-boundary.md) | 先标成 `foreign-summary`，只读观察并写入本轮未接管边界；不要 stage、删除、改写或代提交；提交 notebook 前用 `git diff --cached --name-only` 确认 staged list 只允许 `hermes/YYYY-MM-DD.md` |
| 命令失败、测试失败或前置条件失败后需要改计划 | [`ai-agent-failure-absorption-one-pager.md`](ai-agent-failure-absorption-one-pager.md) | 把失败写成“信号 -> 影响 -> 证据位置”，再决定范围、顺序、目标或交接如何变化 |
| 轻量 proof：小改动需要先证明基础契约，再决定是否跑重型构建 | [`ai-agent-proof-checker-one-pager.md`](ai-agent-proof-checker-one-pager.md) | 设计轻量 preflight 的风险边界、命令顺序和 notebook 句式 |
| 全量 proof：想把 checker 升级成 AGENTS/preflight/CI 候选 | [`ai-agent-full-proof-baseline-one-pager.md`](ai-agent-full-proof-baseline-one-pager.md) | 先建立红绿基线、分类失败项，再决定是否升级为常规必跑项 |
| 统一 preflight：验证命令超过三条，下一轮容易漏跑或报告漂移 | [`ai-agent-preflight-wrapper-one-pager.md`](ai-agent-preflight-wrapper-one-pager.md) | 判断是否该包成 wrapper，固定默认/快速模式、失败标签、编排测试和文档入口边界 |
| proof / baseline / wrapper / 命令梯容易混用，不确定下一份输入该选哪张 | [`ai-agent-proof-to-preflight-decision-table.md`](ai-agent-proof-to-preflight-decision-table.md) | 样本包顶部是 30 秒“验证入口速记”；本表是 2 分钟展开版，用四个问题和决策矩阵判断下一步复制 proof checker、全量基线、wrapper、命令梯还是交接模板 |
| 验证清单太散，需要确定下一条最安全命令 | [`ai-agent-next-safe-command-ladder-one-pager.md`](ai-agent-next-safe-command-ladder-one-pager.md) | 把“跑哪些检查”改写成“当前最大风险 -> 下一条命令 -> pass/fail 语义” |
| 评估报告、发布报告和安全门禁之间字段名开始漂移 | [`ai-agent-evidence-field-handoff-one-pager.md`](ai-agent-evidence-field-handoff-one-pager.md) | 固定 `run_id`、`release_id`、`gate_decision`、`failed_case_ids`、`safe_trace_links` 等字段的生产者、补齐者和消费者 |
| 部分边界没有覆盖，但本轮验证没有失败 | [`ai-agent-unverified-handoff-one-pager.md`](ai-agent-unverified-handoff-one-pager.md) | 拆开已验证事实、未验证原因、结论措辞和下一步第一条动作 |
| 验证被失败阻断，需要把失败证据交给下一轮 | [`ai-agent-verification-failure-handoff-template.md`](ai-agent-verification-failure-handoff-template.md) | 固定“已验证 / 未验证 / 结论措辞 / 下一步 / 证据位置”字段 |
| 最终报告容易漏字段 | [`ai-agent-final-report-field-quickref.md`](ai-agent-final-report-field-quickref.md) | 核对成果、验证、notebook、commit hash、未接管边界和下一段接力点 |
| 想把 AI 编程审查变成固定范围付费交付 | [`ai-agent-audit-report-one-pager.md`](ai-agent-audit-report-one-pager.md) | 用一页纸输出 Scope、Top Risks、下一条安全命令梯、handoff 和 Continue / Narrow / Stop 判断 |
| 想把首份审查报告安全推进成匿名/公开案例 | [`ai-agent-case-publishing-ladder-one-pager.md`](ai-agent-case-publishing-ladder-one-pager.md) | 按证据形状、公开边界和 claim 标签决定 Continue / Narrow / Stop，避免把样板包装成战报 |
| 一条观察看起来值得沉淀成新 skill，但还不确定是否已经可复用 | [`ai-agent-skill-reuse-before-new-skill-one-pager.md`](ai-agent-skill-reuse-before-new-skill-one-pager.md) | 先记录观察快照、复用路径、停止条件和技能化门槛，避免把单次 Narrow 结果误写成新 skill |
| Agent 准备好外发文案或付费 offer，但没有明确发布授权 | [`ai-agent-external-publish-authorization-one-pager.md`](ai-agent-external-publish-authorization-one-pager.md) | 填授权包（渠道、账号、联系路径、观察窗口），缺任一项就不发布；配套 `chapters/ai-agent/external-publish-needs-authorization.md` |
| 发布脚本已经准备接 `--push`，但担心 review note、dry-run sample 或旧日期记录被误用 | [`ai-agent-publish-gate-review-note-one-pager.md`](ai-agent-publish-gate-review-note-one-pager.md) | 填 canonical review note、checker 输出、六个硬门禁和未触发副作用；配套 `chapters/ai-agent/publish-gate-fields-before-push.md` |

### 发布相关场景

只有本轮涉及发布时才使用 [发布门禁一页纸](ai-agent-publish-gate-review-note-one-pager.md)，按缺口查看 review note、readiness 或 fixture 小节。它的生产发布边界不适用于普通文案修订。

## 使用顺序

选择场景 → 复制该输入中的必要部分 → 完成当前目标与相关验证。需要背景时再查 [AI Agent 卡片目录](../chapters/ai-agent/README.md)；不把样本清单当作待办队列。

## 维护检查

新增样本应加入本索引；仅在入口发生变化时同步书籍或章节 README。样本、索引或链接变更后运行 `python3 scripts/verify_tech_cards.py --full-only`，一次覆盖本地链接、卡片计数和样本索引。

样本 verifier 检查本索引是否覆盖所有样本文件、链接是否陈旧，以及样本包声明的 AI Agent 总数与精选卡片数。修改检查脚本本身时再跑对应回归测试。
