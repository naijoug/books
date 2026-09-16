# Tech Cards Handbook Samples

本目录放可复制的 agent 输入、审查样例、一页纸模板和交接片段；它们不是正式卡片，不计入 `chapters/` 的卡片数。维护样本入口时，优先让读者能在 30 秒内回答：我该复制哪一份、它解决哪类接力风险、还需要回到哪张卡片补背景。

术语口径：本目录统一用“验证入口速记”指样本包顶部的 30 秒选择表，用“当前最大风险”作为选择第一列，用“入口判断”指在 proof checker、全量 proof 基线、统一 preflight wrapper、命令梯和交接模板之间只选下一份输入。

## 推荐入口

如果读者是从 AI Agent 章节的「本章四条主线」进入样本区，先按下面的映射缩小范围；样本目录仍以“当前最大风险”选入口，不按文件名机械补齐：

| 主线 | 样本入口 | 适用判断 |
|---|---|---|
| 运行控制 | [`ai-agent-sample-pack.md`](ai-agent-sample-pack.md)、[`ai-agent-dirty-workspace-one-pager.md`](ai-agent-dirty-workspace-one-pager.md) | 需要稳住周期性唤醒、dirty workspace、接力规划和默认动作 |
| 验证与证据 | [`ai-agent-proof-checker-one-pager.md`](ai-agent-proof-checker-one-pager.md)、[`ai-agent-proof-to-preflight-decision-table.md`](ai-agent-proof-to-preflight-decision-table.md)、[`ai-agent-next-safe-command-ladder-one-pager.md`](ai-agent-next-safe-command-ladder-one-pager.md)、[`ai-agent-evidence-field-handoff-one-pager.md`](ai-agent-evidence-field-handoff-one-pager.md) | 需要证明基础契约、选择下一条安全命令、交接未验证边界或统一跨阶段证据字段 |
| 所有权与交付 | [`ai-agent-final-report-field-quickref.md`](ai-agent-final-report-field-quickref.md)、[`ai-agent-external-publish-authorization-one-pager.md`](ai-agent-external-publish-authorization-one-pager.md)、[`ai-agent-publish-gate-review-note-one-pager.md`](ai-agent-publish-gate-review-note-one-pager.md) | 需要核对 commit/report 字段、发布授权、review note 门禁或可公开边界 |
| 产品化阶梯 | [`ai-agent-audit-report-one-pager.md`](ai-agent-audit-report-one-pager.md)、[`ai-agent-case-publishing-ladder-one-pager.md`](ai-agent-case-publishing-ladder-one-pager.md)、[`ai-agent-skill-reuse-before-new-skill-one-pager.md`](ai-agent-skill-reuse-before-new-skill-one-pager.md) | 需要把审查、案例或可复用观察转成收入实验素材 |

验证类样本按两层入口维护：`ai-agent-sample-pack.md` 顶部是 30 秒“验证入口速记”，适合已能说出当前最大风险时直接选下一份输入；`ai-agent-proof-to-preflight-decision-table.md` 是 2 分钟展开版，适合还在 proof checker、全量 proof 基线、统一 preflight wrapper、命令梯和交接模板之间摇摆时再做入口判断。

| 场景 | 先用 | 作用 |
|---|---|---|
| 完整 dirty workspace 接力：周期性唤醒的 Agent 面对 dirty workspace，需要完整 prompt、证据表和最终报告字段 | [`ai-agent-sample-pack.md`](ai-agent-sample-pack.md) | 10 张精选卡片建立最小闭环，附录和配套模板补足执行输入 |
| 只需要一页纸启动一次 dirty workspace 接力 | [`ai-agent-dirty-workspace-one-pager.md`](ai-agent-dirty-workspace-one-pager.md) | 压缩启动快照、归属判断、path-limited 推进和收尾报告 |
| 上一轮点名的目标文件在启动快照里已经 dirty，担心把接力点误当授权 | [`ai-agent-dirty-workspace-one-pager.md`](ai-agent-dirty-workspace-one-pager.md) 的“规划取舍”和 [`../chapters/ai-agent/dirty-target-file-blocks-continuation.md`](../chapters/ai-agent/dirty-target-file-blocks-continuation.md) | 先记录 `blocked continuation`、排除 path 和回归条件，再切到 clean replacement；不要因为它是接力点就顺手修 |
| 共享 `summaries/` 里出现其他 agent notebook，担心 `git add .` 误提交或替对方整理 | [`ai-agent-sample-pack.md`](ai-agent-sample-pack.md) 的“验证入口速记”和卡片 8、9 | 先标成 `foreign-summary`，只读观察并写入本轮未接管边界；不要 stage、删除、改写或代提交 |
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

### 发布门禁三层入口

使用 [`ai-agent-publish-gate-review-note-one-pager.md`](ai-agent-publish-gate-review-note-one-pager.md) 时，先判断当前缺的是哪一层，不要因为 checker 通过就默认进入真实发布：

| 层级 | 先回答的问题 | 缺口表现 | 下一步 |
|---|---|---|---|
| 字段门禁 | review note 是否有 canonical path、同日日期、六个硬门禁 `Go` 和 `Final decision: Publish`？ | 只有 rehearsal / smoke pass，或字段来自自动探测 | 停在 review note，补人工确认字段后重跑 checker |
| readiness 交接 | `readiness.*` / `cron.readiness.*` 是否固定输出 decision、review note、授权、URL、raw freshness、quality 和 remote 字段？ | blocked / skipped / failed 路径缺字段，或 dry-run summary 没写 `publish_authorized=false` | 回到一页纸的“Readiness summary packet”，补字段契约和最小路径矩阵 |
| fixture 门禁 | checker 是否用 dry-run、wrong-date、missing-gate、publish-all-go 等 fixture 验过窄放行语义？ | 只有一条正向 happy path，或阻断 fixture 没检查具体原因 | 先补最小矩阵、共享 helper 和单一 fixture 变量，再接入 `--push` |
| helper 命名 | helper 名字是否区分 `write_*` 证据、`assert_*` 阻断和 `run_*` 受控命令？ | 一个 `run_publish` 同时写证据、改授权、调用 CLI 或检查输出 | 回到一页纸的“Fixture helper 命名约定”，把证据准备、stub 工具、断言和受控命令拆开 |
| 环境边界 | 正向 fixture 是否隔离 token、remote、真实 CLI 和生产 artifact？ | 测试依赖开发机 token / remote / 部署命令才能通过 | 改成临时仓库、stub CLI、本地 fake remote 或 no-op 边界 |

30 秒判断：字段不全时不要写发布命令；readiness summary 不稳定时不要让 cron/report 消费散文日志；fixture 不全时不要把 checker 接入 `--push`；helper 名字看不出证据 / 断言 / 副作用边界时先拆 helper；环境边界不清时，即使 `PUBLISH_ALLOWED` 也只能交付阻塞说明和下一条安全命令。

## 使用顺序

1. **先选主入口**：完整接力用样本包，只做一次短接力用 dirty workspace 一页纸；如果只是因为目录里还有相邻样本没用过而想继续补，请先读 [`../chapters/ai-agent/sample-entry-is-not-todo-queue.md`](../chapters/ai-agent/sample-entry-is-not-todo-queue.md) 停止机械扩表面。
2. **再补风险模板**：失败多就用失败吸收；验证边界不清就先看样本包顶部的“验证入口速记”，按“当前最大风险”做入口判断，再复制 proof checker、全量 proof 基线、统一 preflight wrapper、命令梯或交接模板；需要更细判断时再用 proof 到 preflight 决策表。
3. **最后核对报告字段或商业化样本**：提交后用最终报告字段速查表，确保成果和排除边界同时可接力；如果目标是收入实验，用 AI Coding Audit Report 一页纸把审查压缩成固定范围交付；如果想把交付物公开，先用案例发布阶梯确认材料只能写成匿名案例、公开案例、方法样板还是不发布；如果只是从一次观察想到“要不要新增 skill”，先用 skill 复用一页纸确认是否还应继续复用已有技能。

完整背景阅读见 [`../chapters/ai-agent/README.md`](../chapters/ai-agent/README.md) 的“3 分钟读法”和“快速路径：dirty workspace 心跳接力”。

## 维护检查

- 新增样本时，同步判断是否需要加入本索引、[`../README.md`](../README.md) 的样本包说明，以及 [`../chapters/ai-agent/README.md`](../chapters/ai-agent/README.md) 的配套输入段落。
- 链接或入口文案变更后运行：

```bash
python3 scripts/verify_tech_cards.py
```

其中 `scripts/verify_tech_cards_samples.py` 会检查 `samples/README.md` 是否覆盖所有样本文件、发现指向已删除样本的陈旧链接，并校验 `ai-agent-sample-pack.md` 里的 AI Agent 总数与“精选卡片”数量声明；如果只改样本入口或样本包说明，可先运行这个窄检查，再运行统一 wrapper。
