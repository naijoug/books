# 附录：Agent 上线评审会主持人脚本

> 附录 A 给出空白检查清单，附录 B 给出填完样例。本附录补上评审会现场怎么主持：用 30～60 分钟把证据、风险、范围和下一步压缩成一个可执行的 `pass` / `warn` / `block` 结论。

---

## C.1 适用场景

这份脚本适用于下面几类会议：

- Agent 从内部试用进入灰度前的发布评审。
- Prompt、模型、工具 schema、检索索引或安全回归集有关键变化后的复审。
- 线上事故恢复后，准备重新开放写能力或扩大流量。
- 多团队共同维护同一个工具网关、评估集或发布流水线时的边界对齐。

主持人的目标不是让所有人“感觉放心”，而是确保会议结束时留下四个可复核产物：

1. 候选版本和发布范围。
2. 证据链是否完整。
3. 允许、禁用和需要人工审批的能力边界。
4. 下一次复审或阻断解除条件。

---

## C.2 会前 10 分钟准备

主持人不要把会前准备变成冗长汇报，只需要确认下面材料是否存在。不存在的材料不要在会上临时口头补齐，而是直接标记为缺失证据。

| 材料 | 最小要求 | 缺失时默认处理 |
|---|---|---|
| 候选版本 | `release_id`、`agent_version`、`prompt_hash`、`model_version`、`tool_schema_version` | 不能做 `pass`；最多讨论修复计划 |
| 工具风险表 | 工具名、风险等级、读写属性、owner、默认策略、回滚方式 | 高风险工具不进 allowlist |
| 评估报告 | Golden Tasks 版本、通过/失败样本、失败原因、脱敏 trace | 安全样本缺失或失败默认 `block` |
| 安全门禁材料 | Prompt 注入、越权工具、敏感泄露、失控循环、审批绑定 | 缺硬边界默认 `block` |
| 发布与回滚计划 | 灰度范围、监控阈值、熔断开关、回滚 owner、演练记录 | 不能开放写能力 |

会前可以给参会者发送一句话议程：

```text
本次只回答一个问题：release_id=... 是否可以进入声明范围内的灰度？请所有证据指向版本号、失败样本、safe_trace_links、audit_event_ids 或 runbook；没有证据的项不在会上用主观判断补齐。
```

---

## C.3 30 分钟主持脚本

如果候选变更较小，使用这个 30 分钟版本。每一段超时都要收束为结论，不要让会议滑向自由讨论。

| 时间盒 | 主持人提问 | 必须产出 |
|---|---|---|
| 0-5 分钟 | “本次要发布的确切对象是什么？范围是什么？” | `release_id`、版本字段、目标流量、允许工具和禁用工具 |
| 5-10 分钟 | “工具清单里有没有 L3/L4？审批、deny、回滚在哪里？” | 工具风险表结论；缺 owner、缺审批、缺服务端 deny 的工具移出范围 |
| 10-17 分钟 | “普通回归和安全回归分别失败了什么？失败样本能否重跑？” | `failed_case_ids`、安全样本结论、失败是否进入修复队列 |
| 17-23 分钟 | “日志、trace、审计事件能否支撑复盘且不泄露数据？” | `safe_trace_links`、`audit_event_ids`、未脱敏材料处理结论 |
| 23-27 分钟 | “事故时先按哪个开关？谁负责？多久恢复只读或旧版本？” | 熔断开关、回滚 owner、最大止损时间和演练记录 |
| 27-30 分钟 | “结论是 `pass`、`warn` 还是 `block`？允许范围和下一次检查是什么？” | 最终门禁报告草稿 |

主持人要反复把讨论拉回三个句式：

- “这个判断引用哪个证据？”
- “如果这个证据缺失，允许范围要缩小到哪里？”
- “下一次复审前由谁补齐，补齐标准是什么？”

---

## C.4 60 分钟深度评审脚本

如果涉及高风险写工具、多租户数据、事故恢复或全量放量，使用 60 分钟版本。

### 0-8 分钟：锁定候选变更

主持人逐项确认：

```yaml
release_context:
  release_id: rel_YYYYMMDD_N
  agent_version: agent@x.y.z
  prompt_hash: sha256:...
  model_version: provider/model@date
  tool_schema_version: tools-vN
  golden_tasks_version: golden-vN
  security_suite_version: security-vN
  requested_scope: readonly_canary | approval_required_canary | full_rollout
```

如果说不清候选对象，会议结论不能超过 `block` 或“补材料后重开评审”。

### 8-20 分钟：工具与权限

主持人按风险从高到低提问：

1. 本次是否开放 L3/L4 工具？如果开放，审批是否绑定工具名、参数快照、`args_hash`、资源范围、`idempotency_key` 和过期时间？
2. 是否存在模型绕过工具网关直接访问业务 API 的路径？
3. 工具失败、预算超限、审批过期或参数变化时，系统默认停止、降级还是继续尝试？
4. 每个高风险工具是否有 owner、熔断开关和回滚路径？

结论模板：

```yaml
tool_permission_review:
  decision: pass | warn | block
  allowed_tools: []
  approval_required_tools: []
  blocked_tools: []
  unresolved: []
```

### 20-32 分钟：评估与安全回归

主持人先看安全样本，再看能力样本。不要让“核心任务成功率高”冲淡安全失败。

- Prompt 注入是否覆盖网页、邮件、检索内容和工具返回？
- 越权工具样本是否证明服务端权限层真的拒绝？
- 敏感字段泄露样本是否覆盖最终回答、日志、错误报告和 `safe_trace`？
- 失控循环、工具超时、格式解析失败是否会停止或转人工？

判断规则：安全硬断言失败是 `block`；安全覆盖不足但范围可缩小时是 `warn`；普通能力失败只能在有降级和人工接管时进入 `warn`。

### 32-42 分钟：数据、trace 与审计

主持人抽查证据链是否“够用且不泄露”：

| 检查点 | 通过标准 |
|---|---|
| `safe_trace_links` | 能复盘模型、检索、工具、审批和状态迁移，但不含密钥、支付信息、完整个人数据 |
| `restricted_trace` | 只在事故或安全复盘中短期开放，有审批和访问日志 |
| `audit_event_ids` | 能关联权限拒绝、审批、熔断、人工接管和高风险工具调用 |
| 失败样本 | 已脱敏或合成化，进入版本库不会制造新泄露 |

如果评审材料本身包含未脱敏用户上下文，先处理数据问题，再谈发布。

### 42-52 分钟：监控、熔断与回滚

主持人要求发布 owner 用一句话回答：

```text
如果发布后 15 分钟内出现高风险工具异常、成本飙升、输出格式错误或用户投诉，我们先按哪个开关，谁负责，多久把系统切到只读或上一稳定版本？
```

最低通过标准：

- 有只读模式或停工具开关，不依赖临时改代码。
- 有模型、Prompt、工具 schema 或检索索引回退路径。
- 有 oncall owner 和告警阈值。
- 至少演练过一次关键熔断路径，或本次只能进入更小范围灰度。

### 52-60 分钟：形成结论

主持人把所有争议压缩到一个 YAML 结论：

```yaml
facilitated_release_decision:
  release_id: rel_YYYYMMDD_N
  gate_decision: pass | warn | block
  allowed_scope: readonly_canary | approval_required_canary | full_rollout | blocked
  allowed_tools: []
  approval_required_tools: []
  blocked_tools: []
  evidence:
    failed_case_ids: []
    safe_trace_links: []
    audit_event_ids: []
  warnings: []
  block_reasons: []
  re_review_required_before:
    - condition: "开放 L3 自动执行"
      required_evidence: "审批绑定样例 + 安全回归通过 + 熔断演练记录"
```

会议结束前逐项确认：谁负责写最终报告、报告放在哪里、哪些字段要回写到第 9 章发布报告或流水线 artifact、下一次复审触发条件是什么。

---

## C.5 常见跑偏与主持人纠偏语

| 跑偏信号 | 风险 | 主持人纠偏语 |
|---|---|---|
| “大家都觉得问题不大” | 主观信心替代证据 | “请把这句话翻译成证据链接或门禁字段；没有证据就按缺失处理。” |
| “先全量，上线后再补监控” | 事故时不可止损 | “没有监控和熔断的能力不能全量；我们现在讨论能否缩成只读或内部灰度。” |
| “Prompt 已经写了不要调用高危工具” | 软约束冒充权限边界 | “请指出服务端工具网关的 deny、审批和审计事件；没有就按 `block`。” |
| “trace 只有内部能看” | 内部可见不等于脱敏 | “门禁报告只允许引用 `safe_trace_links`；未脱敏材料先清理再评审。” |
| “这次失败只是边缘 case” | 安全失败被平均值掩盖 | “如果它是 Prompt 注入、越权、泄露或不可回滚写操作，就不是边缘 case，而是硬门禁。” |
| “回滚就是重新部署旧版本” | 中间任务和副作用丢失 | “请说明只读开关、停工具开关、幂等键和已经产生副作用的任务如何处理。” |

---

## C.6 会后交接清单

会议结束后 10 分钟内，把结论写成可被下一位 agent、发布负责人或值班同学接住的交接记录：

```yaml
release_review_handoff:
  release_id: rel_YYYYMMDD_N
  final_decision: pass | warn | block
  report_location: docs/.../release-report.md
  allowed_scope: approval_required_canary
  disabled_scope:
    - full_rollout
    - l4_tools
  next_safe_action:
    owner: support_ai_team
    action: "补齐 coupon.issue 批量滥用样本并重跑 security suite"
    due: 2026-08-24
  next_review_trigger:
    - "security suite 重新通过"
    - "只读/停工具演练完成"
```

交接记录的判断标准很简单：下一位接手的人不需要重新听一遍会议录音，就能知道当前版本允许做什么、不能做什么、为什么、下一步先做哪一件事。

---

## C.7 会后交接填写样例

下面是一份“客服工单 Agent 只读灰度复审”的会后交接样例。它不是会议纪要，而是给下一位接手者的最小行动包：先说明当前结论，再说明允许范围、证据位置、阻断点和下一步命令。

```yaml
release_review_handoff:
  release_id: rel_20260817_support_agent_canary_02
  agent_version: support-agent@1.8.0-rc.3
  prompt_hash: sha256:7f2c...a91e
  model_version: provider/model-2026-08-10
  tool_schema_version: support-tools-v12
  golden_tasks_version: support-golden-v9
  security_suite_version: support-security-v6

  final_decision: warn
  decision_summary: >
    允许 5% 内部工单只读灰度；允许生成建议回复和分类标签；禁止自动发送、退款、改 SLA、批量关闭工单。
    warn 的原因是普通能力回归存在 2 个低频分类错误，但高风险工具仍被服务端 deny，且有人工接管和到期复审。

  allowed_scope:
    traffic: internal_5_percent
    tenants: [internal_support_sandbox]
    tools:
      - ticket.search.readonly
      - ticket.comment.draft
      - knowledge_base.search
    human_approval_required:
      - ticket.comment.publish
  disabled_scope:
    - refund.issue
    - ticket.sla.update
    - ticket.bulk_close
    - external_customer_autosend

  evidence:
    release_report: docs/releases/support-agent/rel_20260817_support_agent_canary_02.md
    eval_run_id: eval_support_20260817_1142
    failed_case_ids:
      - golden_support_037_wrong_priority
      - golden_support_084_missing_escalation_hint
    safe_trace_links:
      - trace/safe/eval_support_20260817_1142/golden_support_037
      - trace/safe/eval_support_20260817_1142/injection_refund_009
    audit_event_ids:
      - audit_tool_deny_refund_issue_20260817_1151
      - audit_approval_required_comment_publish_20260817_1154
    rollback_runbook: docs/runbooks/support-agent-readonly-rollback.md

  warnings:
    - id: warn_priority_taxonomy
      description: "低频分类错误会影响人工队列优先级，但不会触发自动外发或退款。"
      owner: support_ai_eval
      due: 2026-08-20
      exit_criteria: "补 20 个优先级边界样本，重跑 golden-v10，相关失败为 0。"
    - id: warn_escalation_hint
      description: "部分回复草稿缺少升级提示，需在人工审核前标红。"
      owner: support_workflow
      due: 2026-08-21
      exit_criteria: "人工审核 UI 展示 escalation_required 标记，并通过 3 条端到端样例。"

  block_reasons: []
  next_safe_action:
    owner: support_ai_eval
    action: "新增优先级与升级提示边界样本，生成 support-golden-v10，并重跑普通回归与安全回归。"
    command: "pnpm eval:support --suite support-golden-v10 --security support-security-v6 --release rel_20260817_support_agent_canary_02"
    expected_artifact: docs/releases/support-agent/eval_support_20260820.md
  next_review_trigger:
    - "准备把 internal_5_percent 扩到 external_1_percent"
    - "准备开放 ticket.comment.publish 自动执行"
    - "任一 L3/L4 工具 deny、审批或审计策略变化"
```

这份交接样例刻意保留了 `warn` 的约束：它没有说“分类错误可以忽略”，而是把风险压进只读灰度、人工审批、禁用工具、owner、到期日和复审触发条件里。下一位接手者只需要先做 `next_safe_action`，而不是重新争论本轮为什么能灰度。
