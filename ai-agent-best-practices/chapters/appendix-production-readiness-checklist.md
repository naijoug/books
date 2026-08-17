# 附录：Agent 生产就绪检查清单

> 这份清单用于把第 7-10 章的工程控制压缩成一次可执行的上线前核对。目标不是追求“全部完美”，而是让团队知道哪些风险已经被硬边界控制，哪些只能进入只读灰度，哪些必须阻断发布。

---

## A.1 使用方式

建议在每次候选版本进入灰度前，由发布 owner、Agent owner、安全 owner 和业务 owner 共同完成以下四步：

1. **先填事实**：只填写已经存在的证据链接、配置名、版本号和测试结果，不用“应该可以”“大概率没问题”替代证据。
2. **再判门禁**：每一项标为 `pass`、`warn` 或 `block`。`block` 不能被总体成功率抵消；`warn` 必须绑定责任人和到期时间。
3. **最后定范围**：如果不能全量发布，明确是只读灰度、低风险工具灰度、人工审批灰度，还是完全推迟。
4. **回写证据链**：把结论同步到第 9 章发布报告、第 10 章安全门禁报告和事故 runbook，避免评审会后证据散落在聊天记录里。

---

## A.2 一页总表

| 检查域 | 最小证据 | `pass` 标准 | 常见 `block` 信号 |
|---|---|---|---|
| 工具清单 | 工具风险表、owner、环境、回滚方式 | 所有生产工具都有风险等级、owner、默认策略和回滚路径 | 高风险工具没有 owner、不可逆工具没有禁用开关 |
| 权限与审批 | 工具网关策略、审批样例、审计事件 | L3/L4 工具必须经服务端鉴权和参数绑定审批 | 只靠 Prompt 或前端弹窗限制高风险动作 |
| 数据与 trace | 数据分类、脱敏规则、`safe_trace` 样例 | 日志和 `safe_trace` 不含密钥、支付信息、个人高敏字段 | 门禁报告里嵌入未脱敏工具参数或完整用户上下文 |
| Golden Tasks | 普通回归集、安全回归集、失败样本 ID | 安全样本零硬失败；普通失败有解释和降级策略 | Prompt 注入、越权工具、敏感泄露样本失败 |
| 监控与告警 | dashboard、告警阈值、oncall | 成功率、工具失败率、成本、循环次数和高风险拦截都有阈值 | 只能看日志，无法按版本或租户定位异常 |
| 止损与回滚 | 熔断开关、回滚步骤、演练记录 | 能在明确时间窗口内切只读、停工具或回滚版本 | 出事故后需要临时改代码才能停用高风险能力 |
| 发布决策 | 发布报告、`gate_decision`、灰度范围 | 决策可追溯到版本、测试、trace 和审计事件 | 只有“同意上线”的口头结论，没有证据链 |

---

## A.3 工具与权限清单

上线前至少回答这些问题：

- 每个工具是否标注 `risk_level`、读写属性、owner、环境、回滚方式和默认 allow/deny 策略？
- 工具网关是否在服务端校验用户身份、租户边界、工具 allowlist、参数范围和运行期熔断？
- L3/L4 工具是否默认需要审批，且审批绑定工具名、参数快照、资源范围、`args_hash`、`idempotency_key` 和过期时间？
- 当审批过期、参数变化、预算超限或工具失败率异常时，系统是否会拒绝执行而不是继续让模型尝试？
- 是否存在“模型可以直接绕过网关调用业务 API”的路径？如果存在，本次发布应标为 `block`。

推荐门禁结论：

```yaml
tool_permission_gate:
  decision: pass | warn | block
  evidence:
    tool_inventory: docs/.../tool-risk-table.md
    policy_version: tool-gateway-policy-2026-08-17
    approval_sample_ids: [appr_demo_001]
  unresolved:
    - owner: ai_platform
      issue: "补齐低频批量导出工具的回滚说明"
      due: 2026-08-24
```

---

## A.4 数据、日志与 trace 清单

生产 Agent 的泄露风险经常来自“辅助材料”，而不是最终回答本身。评审时要抽样检查：

- Prompt、工具参数、模型输入、日志、错误报告和观测平台是否都执行同一套数据分类与脱敏规则？
- `safe_trace` 是否足够复盘问题，但不包含密钥、身份证、支付信息、完整内部 URL 或未经授权的用户原文？
- `restricted_trace` 是否只在事故调查或安全复盘中短期开放，且有审批和访问日志？
- 门禁报告是否只保存 `safe_trace_links` 和 `audit_event_ids`，而不是直接嵌入敏感上下文？
- 失败样本进入 Golden Tasks 前是否已经合成化或脱敏，避免把真实事故数据复制进仓库？

如果无法证明日志与 trace 已脱敏，应该先降级为只读灰度；如果已发现明文密钥、支付信息或跨租户数据进入评估材料，本次发布应标为 `block` 并先做数据清理。

---

## A.5 评估与门禁清单

一次有效的 Agent 发布评估至少包含三类样本：

1. **能力样本**：核心任务是否完成，输出是否符合 schema，是否能正确使用只读工具。
2. **失败样本**：外部 API 超时、检索无结果、权限不足、格式解析失败时是否能停止、降级或转人工。
3. **安全样本**：Prompt 注入、工具返回注入、越权工具、高风险动作、敏感数据泄露和失控循环。

评估报告的最小字段：

| 字段 | 用途 |
|---|---|
| `release_id` | 绑定本次候选版本和回滚目标 |
| `agent_version` / `prompt_hash` / `model_version` | 定位行为变化来源 |
| `tool_schema_version` | 复现工具参数校验和权限策略 |
| `golden_tasks_version` / `security_suite_version` | 区分能力回归和安全回归 |
| `gate_decision` | 明确 `pass`、`warn` 或 `block` |
| `failed_case_ids` | 让失败可重跑、可复盘、可补测试 |
| `safe_trace_links` | 复盘执行链路，不暴露高敏上下文 |
| `audit_event_ids` | 关联权限拒绝、审批、熔断和人工接管 |

安全样本失败的处理原则：宁可缩小发布范围，也不要用“普通任务成功率很高”掩盖硬边界失效。

---

## A.6 监控、止损与回滚清单

发布前把下面内容变成可执行配置，而不是写在会议纪要里：

- 成功率、P95 延迟、工具失败率、输出格式错误率、平均循环次数、单任务成本、高风险工具拦截率的 dashboard。
- 每个告警对应的 owner、触发阈值、自动动作和人工复盘时间窗口。
- 熔断开关：切只读、暂停单个工具、关闭高成本模型、转人工队列、停止灰度放量。
- 回滚路径：代码、Prompt、模型路由、工具 schema、检索索引和评估集版本分别如何回退。
- 演练记录：至少在低风险环境验证过一次“告警触发 → 自动止损 → 人工复盘 → 恢复”的闭环。

如果一个高风险能力只能通过重新部署代码才能停用，它还不具备生产就绪条件。

---

## A.7 发布决策模板

```yaml
agent_release_decision:
  release_id: rel_YYYYMMDD_N
  agent: support_agent
  scope: readonly_canary | low_risk_tools_canary | approval_required_canary | full_rollout | blocked
  gate_decision: pass | warn | block
  evidence:
    release_report: docs/.../release-report.md
    tool_risk_table: docs/.../tool-risk-table.md
    golden_tasks_report: docs/.../golden-tasks-report.md
    safety_gate_report: docs/.../safety-gate-report.md
    safe_trace_links: []
    audit_event_ids: []
  rollback:
    owner: ai_platform_oncall
    max_time_to_readonly: 5m
    max_time_to_previous_version: 30m
  warnings:
    - owner: ai_safety
      issue: "补齐批量导出场景的安全回归样本"
      due: 2026-08-24
  final_decision_reason: "证据链完整；L3 工具保持审批灰度；未开放 L4 自动执行。"
```

这个模板的价值在于把“能不能上线”变成可审计的工程判断：如果证据为空，结论就不能是 `pass`；如果存在 `block`，发布范围必须收缩到不触发该风险的模式，或者直接推迟。
