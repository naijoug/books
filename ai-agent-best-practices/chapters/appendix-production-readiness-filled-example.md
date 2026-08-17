# 附录：Agent 生产就绪门禁填写样例

> 本样例演示如何把“生产就绪检查清单”填成一份可追责的发布门禁报告。场景是一个客服工单 Agent 准备从内部试用进入 5% 灰度；它可以读取知识库、创建工单、给用户发送草稿回复，但不能自动退款或修改合同。

---

## B.1 发布背景

```yaml
agent_release_decision:
  release_id: rel_20260817_01
  agent: support_ticket_agent
  owner: customer_platform
  scope: approval_required_canary
  gate_decision: warn
  review_time: 2026-08-17 09:30
  reviewers:
    release_owner: customer_platform_oncall
    agent_owner: support_ai_team
    security_owner: ai_safety
    business_owner: support_ops
```

本次不是全量上线，而是“5% 用户、只开放 L1/L2 工具自动执行、L3 工具人工审批”的灰度。`warn` 的含义不是“可以忽略风险”，而是：硬门禁已通过，但仍有明确范围限制和到期整改项。

---

## B.2 工具与权限门禁

| 工具 | 风险等级 | 自动执行策略 | 审批/回滚 | 结论 |
|---|---:|---|---|---|
| `kb.search` | L1 | 允许 | 无需审批；可降级为静态 FAQ | pass |
| `ticket.create` | L2 | 允许 | 失败进入人工队列；可关闭创建入口 | pass |
| `reply.draft` | L2 | 允许生成草稿，不自动发送 | 人工确认后发送；可切只读 | pass |
| `coupon.issue` | L3 | 禁止自动执行；只允许审批后执行 | 审批绑定 `args_hash` 与过期时间；可暂停券发放 | warn |
| `refund.execute` | L4 | 本次不开放 | 工具网关 deny；回滚不适用 | pass |

```yaml
tool_permission_gate:
  decision: warn
  evidence:
    tool_inventory: docs/.../support-agent-tool-risk-table.md
    policy_version: tool-gateway-policy-2026-08-17
    approval_sample_ids: [appr_support_coupon_001, appr_support_coupon_002]
    denied_audit_event_ids: [audit_refund_denied_8841]
  unresolved:
    - owner: support_ai_team
      issue: "补齐 coupon.issue 的批量滥用回归样本"
      due: 2026-08-24
```

判定说明：`refund.execute` 已在服务端网关阻断，不能通过 Prompt 或前端绕过；`coupon.issue` 仍缺少批量滥用样本，因此只允许审批灰度，不能自动执行。

---

## B.3 数据、日志与 trace 门禁

| 检查项 | 证据 | 结论 |
|---|---|---|
| Prompt、工具参数、模型输入统一脱敏 | `safe_trace_links` 中只保留哈希化用户 ID、工单类型和工具名 | pass |
| 错误日志不含密钥和支付信息 | 抽样 50 条错误日志，未发现 token、手机号、银行卡字段 | pass |
| 失败样本可进入 Golden Tasks | 真实工单已合成化，保留意图、权限边界和工具结果结构 | pass |
| restricted trace 访问控制 | 仅安全复盘组可访问，保留审计事件 | pass |

```yaml
data_trace_gate:
  decision: pass
  evidence:
    safe_trace_links:
      - trace://support-agent/rel_20260817_01/safe/0007
      - trace://support-agent/rel_20260817_01/safe/0013
    audit_event_ids:
      - audit_trace_access_2901
      - audit_redaction_rule_1188
```

判定说明：门禁报告只保存脱敏 trace 链接和审计事件 ID，不直接复制用户原文、完整工具参数或内部 URL。

---

## B.4 评估与安全回归门禁

| 样本集 | 版本 | 结果 | 失败处理 | 结论 |
|---|---|---:|---|---|
| 能力回归 | `golden_support_v20260817` | 47/50 通过 | 3 个失败均为知识库无结果，已降级到人工转接 | pass |
| 失败路径 | `failure_support_v20260817` | 20/20 通过 | 外部 API 超时、权限不足、格式解析失败均停止重试 | pass |
| 安全回归 | `security_support_v20260817` | 29/30 通过 | 1 个 coupon 批量滥用样本缺失，不是失败但覆盖不足 | warn |
| 越权工具 | `tool_abuse_v20260817` | 12/12 通过 | `refund.execute` 被网关拒绝并记录审计 | pass |

```yaml
evaluation_gate:
  decision: warn
  evidence:
    release_id: rel_20260817_01
    agent_version: support-agent@0.8.4
    prompt_hash: prompt_sha256_7e3f
    model_version: model-router-2026-08-10
    tool_schema_version: support-tools-2026-08-15
    golden_tasks_version: golden_support_v20260817
    security_suite_version: security_support_v20260817
    failed_case_ids: [cap_kb_empty_003, cap_kb_empty_011, cap_kb_empty_018]
    safe_trace_links:
      - trace://support-agent/rel_20260817_01/safe/eval-summary
    audit_event_ids:
      - audit_refund_denied_8841
```

判定说明：普通能力失败已进入人工降级，不阻断只读/审批灰度；安全覆盖缺口会限制发布范围，直到补齐 `coupon.issue` 批量滥用样本后才允许更高比例灰度。

---

## B.5 监控、止损与回滚门禁

| 机制 | 配置 | 自动动作 | 结论 |
|---|---|---|---|
| 成功率告警 | 15 分钟窗口低于 92% | 暂停放量，通知 oncall | pass |
| 工具失败率告警 | L2 工具失败率超过 5% | 切换到草稿模式，不创建工单 | pass |
| 成本止损 | 单任务成本超过预算 2 倍 | 降级到低成本模型并减少重试 | pass |
| 循环止损 | 单任务超过 6 次工具调用 | 强制停止并转人工 | pass |
| 高风险工具拦截 | L3/L4 拒绝率异常上升 | 关闭对应工具 allowlist | pass |

```yaml
rollback:
  owner: customer_platform_oncall
  max_time_to_readonly: 5m
  max_time_to_previous_version: 30m
  switches:
    readonly_mode: feature.support_agent.readonly
    disable_coupon_tool: feature.support_agent.coupon_issue.enabled
    model_route: config.support_agent.model_route
  drill_record: drill_support_agent_readonly_20260816
```

判定说明：本次发布可以不重新部署代码就切只读、停用 `coupon.issue`、回退模型路由；因此具备灰度止损条件。

---

## B.6 最终决策

```yaml
final_gate_report:
  release_id: rel_20260817_01
  gate_decision: warn
  allowed_scope: approval_required_canary
  rollout_limit:
    traffic_percent: 5
    auto_tools: [kb.search, ticket.create, reply.draft]
    approval_required_tools: [coupon.issue]
    blocked_tools: [refund.execute]
  warnings:
    - owner: support_ai_team
      issue: "补齐 coupon.issue 批量滥用安全回归样本，并在下一次灰度前重跑 security_support_v20260817"
      due: 2026-08-24
  block_conditions:
    - "安全样本出现 Prompt 注入成功、越权工具执行或敏感字段泄露"
    - "coupon.issue 未经审批被执行"
    - "无法在 5 分钟内切换到只读模式"
  final_decision_reason: "工具网关、脱敏 trace、评估报告、监控止损和回滚开关证据链完整；但 L3 工具覆盖不足，因此只允许审批灰度，不允许全量或自动发券。"
```

这份样例的核心是把风险变成范围控制：不是因为存在 `warn` 就一律阻断，也不是因为核心能力通过就强行上线；真正的工程判断是把每个证据缺口绑定到更小的发布范围、更强的人工审批和明确的到期整改。

---

## B.7 反例：不能把 `block` 包装成 `warn`

评审会上最危险的写法，不是明确说“还不能上线”，而是把缺失硬边界的风险写成“后续优化”。下面这份错误结论看起来格式完整，但实际应该阻断发布：

```yaml
bad_gate_report:
  release_id: rel_20260817_bad
  gate_decision: warn
  scope: full_rollout
  evidence:
    golden_tasks_pass_rate: "96%"
    safety_suite_version: security_support_v20260817
  known_issues:
    - "refund.execute 目前只在 Prompt 中要求模型不要调用，服务端网关策略下周补"
    - "trace 中偶尔包含完整用户消息，暂时只限制内部人员查看"
    - "没有只读开关；如遇事故由值班同学临时回滚部署"
  final_decision_reason: "核心能力成功率较高，风险可接受，先全量上线再补控制。"
```

这份报告至少有三个硬阻断点：

| 问题 | 为什么是 `block` | 正确处理 |
|---|---|---|
| 高风险退款工具只靠 Prompt 约束 | 模型输出不是权限边界；一旦被注入或误判，就可能直接触发不可逆动作 | 在服务端工具网关默认 deny，补审批、`args_hash`、幂等键和审计事件后再评审 |
| trace 含完整用户消息 | 门禁材料本身变成新的数据泄露面；“内部可见”不能替代脱敏 | 先清理历史材料，补 `safe_trace`，把 restricted trace 放进短期审批流程 |
| 没有只读或停工具开关 | 事故时只能重新部署，止损时间不可控 | 先实现只读、停工具、模型路由回退等开关，并完成一次演练 |

可以把它改成下面的阻断结论：

```yaml
corrected_gate_report:
  release_id: rel_20260817_bad
  gate_decision: block
  allowed_scope: blocked
  block_reasons:
    - "L4 refund.execute 缺少服务端 deny/审批策略"
    - "门禁证据中仍存在未脱敏用户上下文"
    - "缺少只读和停工具止损开关，无法满足事故响应时间"
  required_before_re_review:
    - owner: support_ai_team
      issue: "上线工具网关策略并补充 refund.execute 越权回归样本"
    - owner: ai_safety
      issue: "清理评估材料并产出 safe_trace 抽样证明"
    - owner: customer_platform_oncall
      issue: "实现只读/停工具开关并记录一次回滚演练"
```

判断 `warn` 和 `block` 的简单边界是：`warn` 可以通过缩小范围、加强审批、限定时间来控制；`block` 则表示系统缺少硬边界，继续发布会让模型、日志或人工流程拥有不可接受的破坏面。只要风险仍依赖“模型会听话”“值班同学会及时发现”“内部人员不会误用”这类软假设，就应该先写成 `block`。
