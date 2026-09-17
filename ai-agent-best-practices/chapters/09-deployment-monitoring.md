# AI Agent 最佳实践指南

## 第九章：部署与监控 —— 让 Agent 在生产环境可恢复、可观测、可控

> Agent 上线后最大的挑战不是“能不能回答”，而是失败时能不能定位、止损和恢复。

---

## 9.1 部署前先定义运行形态

Agent 系统常见有三种运行形态：

| 形态 | 示例 | 部署重点 |
|------|------|----------|
| 同步 API | 聊天助手、客服、内部问答 | 低延迟、限流、快速失败 |
| 异步任务 | 文档处理、调研报告、代码迁移 | 队列、幂等、暂停恢复、状态持久化 |
| 人机协作工作流 | 审批、运维、财务、销售跟进 | 人工确认、审计、权限、通知 |

不要把长时间任务塞进普通 HTTP 请求里。超过几十秒的任务应进入队列，由 worker 执行，并把状态写入数据库。

---

## 9.2 推荐部署架构

```text
用户入口
  ↓
API Gateway / Web App
  ↓
权限与速率限制
  ↓
Agent Orchestrator
  ├─ 会话状态 / checkpointer
  ├─ 工具网关 / 权限策略
  ├─ 模型路由 / 成本预算
  └─ 任务队列 / worker
        ↓
业务系统、检索系统、外部 API
        ↓
日志、指标、执行 trace、审计日志、离线评估
```

核心原则：

1. 编排层负责状态、权限和恢复，不要把这些逻辑散落在 Prompt 里。
2. 工具调用通过工具网关，统一做鉴权、参数校验、脱敏、超时和审计。
3. 长任务必须支持任务 ID、状态查询、重试、取消和人工接管。

---

## 9.3 容器化与配置

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "agent_server"]
```

部署配置要区分：

- **代码配置**：工具注册、工作流拓扑、默认模型路由。
- **环境配置**：API key、数据库地址、模型供应商、区域。
- **运行策略**：预算、限流、最大步骤数、工具超时、审批开关。

不要把密钥、用户数据、生产 URL 写进 Prompt 或代码仓库。

---

## 9.4 可观测性

### 9.4.1 日志、指标和执行 trace

| 类型 | 必须记录 | 作用 |
|------|----------|------|
| 日志 | 请求 ID、用户/租户、任务状态、错误分类 | 排查单次失败 |
| 指标 | 成功率、延迟、token、工具调用、成本、重试 | 发现趋势和异常 |
| 执行 trace | 模型调用、检索、工具、审批、状态迁移 | 还原完整执行链路 |
| 审计 | 高风险工具参数、审批人、执行结果 | 合规和追责 |

示例指标：

```text
agent_task_success_total{agent="support", status="success"}
agent_task_duration_seconds_bucket{agent="support"}
agent_tool_call_total{tool="crm_update", result="blocked"}
agent_model_tokens_total{model="frontier", direction="input"}
agent_human_approval_total{decision="approved"}
```

### 9.4.2 Agent 特有监控

普通 Web 服务监控不够，还要监控：

- 平均步骤数和最大步骤数触发次数。
- 工具调用失败率和超时率。
- 高风险工具被拦截次数。
- 人工审批等待时间。
- 模型拒答率、误拒率和输出格式错误率。
- 检索命中率、rerank 后命中率和无结果率。
- 单任务成本和租户级预算消耗。

### 9.4.3 生产监控指标清单

上线前要把“看什么、谁负责、超过什么阈值就处理”写成表，而不是等事故发生后再临时翻日志。

| 指标 | 计算方式 | 建议阈值 | 责任动作 |
|------|----------|----------|----------|
| 任务成功率 | `success / total`，按 agent、租户、任务类型分组 | 核心任务 30 分钟低于 95% 告警 | 暂停新版本灰度，抽样失败任务的脱敏执行 trace |
| 工具失败率 | `tool_error / tool_call`，区分超时、鉴权、参数错误 | 单工具 10 分钟高于 3% 告警 | 降级工具、检查 schema 和外部 API |
| 人工接管率 | `human_takeover / total` | 较 7 日均值翻倍告警 | 分析意图识别、权限策略和高危分支 |
| 高风险拦截率 | `blocked_high_risk / high_risk_attempt` | 任意突增或连续非零需复盘 | 进入只读模式，审计被拦截参数 |
| P95 端到端延迟 | 从入口请求到最终状态完成 | 同步入口超过 SLA 20% 告警 | 切换快模型、降低检索深度或转异步 |
| 平均循环次数 | 每个任务的模型-工具循环轮数 | 接近 `max_steps` 的任务超过 5% 告警 | 检查 Prompt、工具返回和停止条件 |
| 单任务成本 | token、检索、工具和人工成本合计 | 超过预算 20% 告警 | 启用预算熔断或模型路由降级 |
| 输出格式错误率 | JSON/schema/结构化输出解析失败占比 | 高于 1% 告警 | 收紧响应 schema，补回归样本 |

这些指标要同时进入 dashboard、告警规则和发布报告。最低要求是每次灰度放量前后对比同一组指标：如果成功率提升但成本、人工接管或高风险拦截同步恶化，仍然不能直接放量。

---

## 9.5 告警与自动止损

```yaml
groups:
  - name: agent_alerts
    rules:
      - alert: AgentTaskFailureRateHigh
        expr: rate(agent_task_failed_total[10m]) / rate(agent_task_total[10m]) > 0.05
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Agent 任务失败率超过 5%"

      - alert: HighRiskToolBlockedSpike
        expr: increase(agent_tool_call_blocked_total{risk="high"}[15m]) > 20
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "高风险工具拦截数量异常升高"
```

告警不应该只通知人，还应该触发自动止损：

1. 暂停高风险工具。
2. 降级到只读模式。
3. 切换到保守模型或备用供应商。
4. 限制单用户/单租户并发。
5. 把任务转人工队列。

### 9.5.1 指标异常到止损动作的 runbook

告警规则只解决“什么时候响”，runbook 要解决“响了以后系统先做什么、人在什么时间窗口内复盘什么”。建议把自动动作写成可配置策略，并为每次触发生成一条事故记录。

| 异常信号 | 自动止损动作 | 人工复盘重点 | 恢复条件 |
|----------|--------------|--------------|----------|
| 高风险工具拦截突增 | 立即暂停写操作工具，保留只读查询和人工审批入口 | 抽查被拦截参数、租户来源、Prompt 版本和工具 schema 版本 | 连续 30 分钟无新增异常，且抽样脱敏执行 trace 确认为误触发或已修复 |
| 工具失败率超过阈值 | 将该工具从自动链路中摘除，改为返回“待人工处理”状态 | 区分外部 API 故障、鉴权失效、参数 schema 漂移和超时 | 工具健康检查通过，回放最近失败样本成功率达到门禁 |
| 平均循环次数接近 `max_steps` | 降低单任务最大步数，关闭高成本模型路由，必要时转人工队列 | 检查停止条件、工具返回是否可行动、Prompt 是否鼓励继续尝试 | Golden Tasks 中循环类失败回归通过，生产 P95 步数回到基线 |
| 单任务成本快速上升 | 启用预算熔断，切换到便宜模型或减少检索深度 | 对比 token、检索次数、重试次数和人工接管变化 | 单任务成本回落到预算内，成功率和安全指标未恶化 |
| 输出格式错误率升高 | 切换到严格 schema 响应或旧版本 Prompt，阻断需要结构化结果的写操作 | 检查模型版本、response schema、解析器和失败样本分布 | 解析失败率低于阈值，离线回放新增失败样本通过 |

runbook 还要规定事故记录的最小字段：`incident_id`、告警名、触发指标、自动动作、影响租户、关联 `trace_id` 或脱敏执行 trace 链接、版本信息、负责人、恢复时间和后续修复任务。这样每次止损都会反哺离线评估集，而不是只在群里留下一串告警截图。

### 9.5.2 事故回放演练：把线上异常变成下一次发布门禁

自动止损只能降低当下损失，真正的能力提升来自回放：能不能把一次线上异常压缩成可重跑、可脱敏、可进入门禁的样本。每次 P1/P2 事故、人工接管激增或高风险工具被熔断后，都应该在恢复完成后做一次 30 分钟事故回放演练，而不是只写“已修复”。

建议把演练拆成五步：

1. **定位候选版本**：用 `release_id`、`agent_version`、`prompt_hash`、`model_version` 和 `tool_schema_version` 锁定事故发生时的候选组合。
2. **选择最小失败链路**：从原始日志中挑一条能复现问题的任务，保留 `task_id`、状态迁移、工具调用、审批记录和审计事件；真实用户内容只进入受限材料。
3. **生成脱敏回放样本**：把个人数据、密钥、客户名称和业务机密替换成合成值，保留会触发问题的结构、权限边界和工具返回形态。
4. **回放候选修复**：先在旧版本确认样本失败，再在修复版本确认通过；如果只能在人工环境复现，至少要留下执行步骤、期望断言和 `safe_trace_links`。
5. **接入发布门禁**：把样本放回第 8 章的 `evals/golden/` 或 `evals/security/`，并在第 10 章安全门禁报告里记录新增 `failed_case_ids` 已经回归通过。

一条合格的事故回放样本不需要暴露真实客户上下文，但必须保留能触发问题的边界条件。最小记录可以写成下面这样：

```yaml
incident_replay:
  incident_id: "inc-2026-08-20-001"
  source_alert: "HighRiskToolBlockedSpike"
  release_id: "agent-support-2026-08-20-rc1"
  sanitized_case_id: "SEC-tool-return-injection-003"
  original_trace_access: "restricted_trace://inc-2026-08-20-001/task-42"
  safe_trace_links:
    - "safe_trace://inc-2026-08-20-001/replay/SEC-tool-return-injection-003"
  regression_target: "evals/security/SEC-tool-return-injection-003.yaml"
  expected_assertions:
    - "不得调用 delete_project"
    - "工具网关记录 tool_return_injection"
    - "最终状态进入 awaiting_human_review"
  gate_decision_after_fix: "pass"
```

如果事故回放无法生成样本，发布 owner 要在复盘里写清原因：是缺少脱敏 trace、版本字段不完整、工具返回未落库，还是审计事件无法关联。这个缺口本身也要进入发布清单；否则下一次同类事故仍然只能靠人肉记忆处理。

---

## 9.6 弹性与恢复

### 9.6.1 重试必须分类

```python
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class TransientToolError(Exception):
    pass


@retry(
    retry=retry_if_exception_type(TransientToolError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
)
def call_unstable_tool(args):
    return tool.invoke(args)
```

不要对所有错误无脑重试。权限错误、参数错误、预算超限和安全拦截应该立即停止或交给人。

### 9.6.2 幂等与状态恢复

写操作工具必须支持幂等键：

```python
def send_invoice_email(invoice_id: str, recipient: str, idempotency_key: str):
    if audit_log.exists(idempotency_key):
        return audit_log.get_result(idempotency_key)

    result = email_provider.send(invoice_id, recipient)
    audit_log.record(idempotency_key, result)
    return result
```

长任务要能从最后一个安全 checkpoint 恢复，而不是失败后从头执行所有工具。

---

## 9.7 发布、灰度和回滚

Agent 变更不只是代码变更，还包括模型、Prompt、工具描述、检索索引和评估集。

进入本节前，先回到根目录 `README.md` 的 [90 分钟上线前审查工作流](../README.md#90-分钟上线前审查工作流) 统一灰度和门禁术语：只读灰度只允许读工具和草稿能力，人工审批灰度才允许部分写工具在服务端审批后执行；`warn` 只能表示硬边界存在但范围受限，缺少审批、审计、脱敏 trace 或回滚能力时必须写成 `block`。如果团队只说“小流量灰度”，发布报告还要继续追问“开放的是读能力、写能力，还是人工审批后的写能力”。

上线流程建议：

1. 离线评估集通过。
2. 影子流量对比旧版本和新版本。
3. 小比例灰度，只开放低风险任务。
4. 监控成功率、成本、延迟、人工介入和安全拦截。
5. 达到阈值后逐步放量。
6. 保留一键回滚到旧 Prompt、旧模型路由和旧工具版本的能力。

### 9.7.1 发布准入与回滚清单

Agent 发布清单要同时覆盖代码、模型、Prompt、工具和数据。不要只记录“部署了某个 Git commit”，否则线上异常时很难还原到底是哪一层变化导致。

| 阶段 | 准入检查 | 必须记录 | 失败时动作 |
|------|----------|----------|------------|
| 离线评估 | Golden Tasks 全量通过，核心任务集不低于门禁，禁止动作违规率为 0 | 代码版本、Prompt 哈希、模型版本、工具 schema 版本、评估集版本 | 阻断发布，把失败样本转为修复任务 |
| 影子流量 | 新旧版本在真实请求副本上对比，不能执行真实写操作 | 请求采样规则、旧版本指标、新版本指标、差异报告 | 只保留日志，不进入灰度 |
| 1% 灰度 | 只开放低风险租户和低风险工具，观察至少一个完整业务周期 | 灰度租户、灰度比例、启用工具列表、开始时间 | 自动降回旧版本，保留脱敏执行 trace 供复盘 |
| 逐步放量 | 成功率、成本、P95 延迟、人工接管率和安全拦截均不劣于基线 | 每次放量比例、负责人、指标快照、审批记录 | 暂停放量，回到上一稳定比例 |
| 全量后观察 | 继续保留旧 Prompt、旧模型路由和旧工具版本一段时间 | 回滚入口、旧版本保留期限、数据兼容说明 | 一键回滚，并运行回滚后验证清单 |

这张表中的灰度和回滚字段应直接回填到 [附录 A：生产就绪检查清单](appendix-production-readiness-checklist.md) 的监控 / 回滚区：灰度租户、工具 allowlist、禁用范围、`safe_trace_links`、告警 owner、版本开关、能力开关和流量开关都要能被下一位值班同学复核。若只读灰度没有写清被禁用的写工具，或人工审批灰度没有绑定审批参数快照、幂等键和审计事件 ID，应先按 [附录 B：生产就绪门禁填写样例](appendix-production-readiness-filled-example.md) 校准为 `warn` 或 `block`，不要把“稍后补充”写成发布通过。

回滚不能只依赖人工改配置。至少准备三类开关：

- **版本开关**：把模型路由、Prompt 模板、工具 schema 和检索索引切回上一稳定版本。
- **能力开关**：关闭写操作工具、高风险工具或自动执行，只保留只读回答和人工审批。
- **流量开关**：按租户、任务类型、用户分组或风险等级降低新版本流量。

回滚后还要验证三件事：失败率是否回到基线、是否还有未完成任务卡在新旧版本之间、事故样本是否已经进入离线评估集。没有这三项验证，回滚只是“看起来停止部署”，不等于系统已经恢复。

### 9.7.2 未完成任务的迁移、取消与重放

回滚时最容易被忽略的是“已经跑到一半的任务”。如果新版本已经写入中间状态、拿到人工审批或调用过外部工具，简单把流量切回旧版本可能制造重复执行、状态丢失或用户看不到结果的问题。

建议把长任务状态设计成可判定的迁移点：

| 任务状态 | 默认处理 | 必须检查 | 用户可见反馈 |
|----------|----------|----------|--------------|
| `queued` | 重新路由到旧版本 worker | 队列消息是否携带目标版本和幂等键 | 一般无需通知，保持预计开始时间 |
| `running_readonly` | 从最近 checkpoint 重放到旧版本 | 检索结果、模型中间结论和工具输出是否可兼容 | 显示“任务已切换到稳定版本继续执行” |
| `awaiting_approval` | 保留审批单，冻结自动继续执行 | 审批内容是否绑定旧 Prompt/工具 schema | 提醒审批人重新确认高风险动作 |
| `running_write_tool` | 不自动重放，先进入人工复核队列 | 幂等键、外部系统执行结果、审计日志 | 告知用户任务进入安全复核 |
| `failed_after_write` | 禁止自动重试，生成补偿任务 | 是否需要撤销、补发或对账 | 给出明确状态和后续处理时限 |

实现上，任务记录至少要保存 `task_id`、`agent_version`、`prompt_hash`、`tool_schema_version`、`checkpoint_id`、`idempotency_key`、`last_safe_step` 和 `side_effects`。回滚程序只能从 `last_safe_step` 之后继续，且遇到 `side_effects` 非空的任务必须走人工或补偿流程。

可以把恢复动作分成三类：

1. **迁移**：状态和工具输出完全兼容，直接把后续步骤交给旧版本继续。
2. **取消**：任务尚未产生副作用，向用户返回可重试状态，并保留脱敏执行 trace 供排查。
3. **重放**：只对只读步骤或具备幂等键的写操作执行，重放前先检查审计日志，避免重复发邮件、重复扣款或重复创建记录。

这张表要和发布清单一起演练。只有确认“新版本暂停后，旧版本能接住哪些任务，哪些任务必须人工处理”，回滚才是真正可操作的恢复能力。

### 9.7.3 把发布流程交给第十章的安全门禁

第九章关注“能不能安全部署、监控和回滚”，第十章会进一步定义“哪些风险根本不允许放量”。因此发布流水线里要给安全门禁留出独立阶段，而不是把它混在普通成功率指标里：

```text
代码/Prompt/工具变更
  ↓
普通 Golden Tasks 回归
  ↓
安全回归集（Golden Tasks 的 `security` 子集）硬门禁
  ↓
影子流量与只读灰度
  ↓
小比例写能力灰度
  ↓
逐步放量与事故熔断 runbook 演练
```

这条链路有三个关键约束：第一，安全回归集失败不能被平均成功率抵消；第二，影子流量和早期灰度默认只开放只读工具，写能力要等高风险审批、审计和熔断开关都验证通过后再开放；第三，每次回滚或事故复盘后，都要把新增失败样本回填到第八章的评估集和第十章的安全门禁中。

为了让第九章的发布报告能被第十章的安全门禁直接复用，发布流水线至少要输出同一组字段：`release_id`、`agent_version`、`prompt_hash`、`model_version`、`tool_schema_version`、`golden_tasks_version`、`security_suite_version`、`gate_decision`、`failed_case_ids`、`safe_trace_links` 和 `audit_event_ids`。普通灰度报告可以只展示摘要，但原始记录必须保留这些字段；否则门禁失败后只能靠聊天记录和截图复盘，无法追溯到底是 Prompt、模型、工具 schema 还是评估集变化放宽了边界。

落地时可以把这些字段当作发布报告的消费顺序：先用 `release_id` 和版本字段定位候选变更，再用 `gate_decision` 和 `failed_case_ids` 判断是否允许继续灰度，然后打开 `safe_trace_links` 复盘失败路径，最后通过 `audit_event_ids` 核对权限拒绝、审批、熔断和人工接管是否符合第十章的安全策略。这样读者不只是“保存字段”，而是能在发布会、事故复盘或回滚评审中按同一条证据链行动。

这样第八章的测试资产、第九章的发布能力和第十章的安全控制就形成闭环：测试发现退化，发布流程阻断风险，监控与 runbook 把线上异常再反哺为新的回归样本。

### 9.7.4 发布报告模板：把 `gate_decision` 变成可执行结论

发布报告不应该只是“这次部署了什么”的流水账，而应该是第 8 章评估结果、第 9 章灰度监控和第 10 章安全门禁共同消费的证据包。建议把报告固定成机器可读结构，让 CI、发布会和事故复盘使用同一份 artifact。第 8 章 8.5.3 已经给出评估产出到发布字段再到安全门禁的映射表；这里的报告模板就是那张映射表的发布侧落点。若团队需要会议中可直接填写的版本，可以先使用 `docs/` 的 [Agent 上线前 90 分钟审查模板](../../../docs/documents/trending/ai/agent-release-90-minute-review-template.md) 收集字段，再用 [Agent 发布证据字段映射表](../../../docs/documents/trending/ai/agent-release-evidence-field-map.md) 检查字段断链，最后用 `skills/` 的 [Agent Release Gate 技能](../../../skills/skills/manual/review/agent-release-gate/) 把证据压缩为 `pass` / `warn` / `block` 门禁报告。写报告前先用技能里的 [Quick Reference](../../../skills/skills/manual/review/agent-release-gate/references/quick-reference.md) 对齐可复现对象、硬门禁和 `warn` 范式；如果 `warn` 的允许范围、禁用范围或 re-entry 条件写不清，参考 [filled example](../../../skills/skills/manual/review/agent-release-gate/references/filled-example.md) 后再落入下面的发布报告。书内读者也可以直接沿附录使用：先用 [附录 A：生产就绪检查清单](appendix-production-readiness-checklist.md) 收集发布事实，再用 [附录 B：生产就绪门禁填写样例](appendix-production-readiness-filled-example.md) 校准 `warn` / `block` 写法，最后让主持人按 [附录 C：上线评审会主持人脚本](appendix-release-review-facilitator-script.md) 在会议中收束证据、范围和下一次复审条件：

```yaml
release_report:
  release_id: "agent-support-2026-07-16-001"
  owner: "agent_release_owner"
  agent_version: "2026.07.16"
  prompt_hash: "sha256:..."
  model_version: "provider/model@2026-07-15"
  tool_schema_version: "tools-support-v18"
  golden_tasks_version: "golden-support-v42"
  security_suite_version: "security-agent-v11"
  gate_decision: "warn" # pass | warn | block
  decision_reason: "只读灰度通过；写操作审批参数绑定仍缺 2 个样例"
  rollout_scope:
    tenant_group: "internal-beta"
    traffic_percent: 1
    allowed_tools:
      - "kb_search"
      - "ticket_summarize"
    blocked_tools:
      - "crm_update"
  evidence:
    failed_case_ids:
      - "SEC-approval-parameter-binding-002"
    safe_trace_links:
      - "safe_trace://release/agent-support-2026-07-16-001/SEC-approval-parameter-binding-002"
    audit_event_ids:
      - "audit_01HX..."
  rollback:
    version_switch: "prompt:model:tools -> previous_stable"
    capability_switch: "disable_write_tools"
    traffic_switch: "beta -> 0%"
    owner: "agent_oncall"
  next_review:
    required_before_write_gray: true
    tasks:
      - "补齐写操作审批参数绑定样例并重跑安全回归集"
      - "演练 crm_update 熔断后人工接管路径"
```

模板写完后，不要只把它归档在发布流水线里。`rollout_scope` 应复制到 [附录 C：上线评审会主持人脚本](appendix-release-review-facilitator-script.md) 的 `allowed_scope` / `disabled_scope`，说明当前版本到底允许哪些租户、流量和工具；`rollback` 应复制到会后交接的 `rollback_runbook` 或下一步命令，说明谁能在告警后执行版本开关、能力开关和流量开关；`next_review` 应落成 `next_safe_action` 和 `next_review_trigger`，让下一位接手者知道“开放写能力前还差哪条证据”。如果这三个字段只停留在发布报告里，值班同学仍然要回会议记录里猜允许范围、回滚 owner 和复审条件。

消费这份报告时，先看 `gate_decision`，再决定能做什么：

| 结论 | 发布动作 | 必须留下的证据 |
|------|----------|----------------|
| `pass` | 允许按灰度计划开放声明范围内的工具；高风险写能力仍按审批策略执行 | 完整评估结果、监控基线、回滚开关和第 10 章安全清单通过记录 |
| `warn` | 只能只读灰度、内部灰度或人工接管灰度；不得扩大到高风险写操作 | 未满足项、负责人、补齐期限、失败样本 ID 和下一次复审条件 |
| `block` | 阻断发布，冻结候选 Prompt/模型/工具 schema 组合 | 阻断原因、失败 trace、审计事件、回滚或修复任务、重新进入门禁的条件 |

这样做的收益是把“能不能上线”的争论转成可执行分支：`pass` 进入灰度，`warn` 降级范围并设复审条件，`block` 回到修复队列。第十章 10.9 的发布前安全检查清单产出的结论，必须回写到这里的 `gate_decision` 和 `decision_reason`，否则监控、回滚和值班人员无法知道当前版本到底被允许执行哪些能力。

### 9.7.5 Readiness 字段契约：让无人值守发布可接力

当发布流程由 cron、CI 或 Agent 自动触发时，发布报告还需要一层更细的 `readiness.*` 字段契约。它和上面的 `release_report` 不冲突：`release_report` 面向评审会和事故复盘，回答“这个版本能不能进入哪个范围”；`readiness.*` 面向脚本、日志和下一位接手者，回答“当前自动流程停在哪一步，下一条安全动作是什么”。如果只写一段自然语言日志，下一轮 Agent 很容易把 dry-run、缺人工授权、质量门禁失败和已发布混在一起。

最小字段可以按下面方式设计：

| 字段 | 作用 | 示例取值 |
|------|------|----------|
| `readiness.status` | 总状态，先判断是 ready、blocked、skipped、failed 还是 published | `blocked` |
| `readiness.reason` | 为什么停住或失败 | `quality_gate_failed`、`publish_blocked` |
| `readiness.next_action` | 下一条安全动作，不让接手者猜 | `open review note and request human go` |
| `readiness.push` | 本轮是否请求真实推送 | `false` / `true` |
| `readiness.human_review_go` | 人工复核是否明确授权 | `false` / `true` |
| `readiness.publish_authorized` | 是否满足发布授权硬门禁 | `false` / `true` |
| `readiness.review_note_path` | 本轮复核记录位置 | `docs/ai-daily-publish-review-2026-08-07.md` |
| `readiness.review_note_canonical` | 复核记录是否位于约定路径 | `not_required` / `mismatch` / `matched` |
| `readiness.public_url` | 已发布后的外部可见入口 | `missing` 或 URL |
| `readiness.git_remote_origin` | 本地发布对象能否追溯到远端仓库 | `missing` 或 remote URL |

这组字段的关键不是“多记录一些日志”，而是把发布状态变成稳定接口：human-readable summary 可以改写，`key=value` 或 JSON 字段名不要随意漂移。尤其是 `publish_authorized=false`，它不是失败，而是没有人工授权时的正确停点。Agent 可以准备证据、生成 review note、跑质量门禁，但不能把 dry-run 结果伪装成已经发布。

把契约落到测试时，至少覆盖五条路径：

1. **dry-run 成功但未授权**：断言 `push=false`、`publish_authorized=false`、`review_note_canonical=not_required`。
2. **push 但缺 review note**：断言 `review_note_path=`、`human_review_go=false`、`publish_authorized=false`。
3. **review note 路径不规范**：断言 `review_note_path=<传入路径>`、`review_note_canonical=mismatch`。
4. **质量或新鲜度门禁失败**：断言 `status=failed`、失败详情和下游检查 `not_checked`，证明不会继续发布。
5. **发布成功**：断言 `status=published`、`public_url`、`git_remote_origin`，证明结果可复核。

实施顺序也要保守：先从 checklist 抽字段，再跑现有测试确认 green，然后一次只补一个路径的断言。只有脚本真实输出发生变化时才改文档；不要先在文档里幻想字段，再倒逼脚本输出。若团队需要把这套方法迁移到非 Agent 项目，可参考 `docs/` 中的 [Readiness Field Contract](../../../docs/documents/trending/ai/readiness-field-contract.md)，但书内读者只要记住一句话：无人值守发布的日志必须能回答“停点、原因、证据、授权、下一步”，否则自动化越多，接力成本越高。

### 9.7.6 无人值守任务交接日志：先保护现场，再继续推进

许多团队会把 Agent 放进定时任务、CI 或夜间批处理里，让它定期整理 backlog、生成文档、跑回归或准备发布材料。真正危险的不是“它没有做完”，而是下一轮 Agent 看不懂上一轮到底停在什么状态，于是把别人的未提交改动当成自己的成果、把缺授权当成失败重试、或把 dry-run 当成已经发布。无人值守任务的日志必须先保护现场，再描述推进。

可以把每轮日志固定成四段：

| 段落 | 必填问题 | 目的 |
|------|----------|------|
| 当前状态 | 启动时哪些 repo clean，哪些已有 dirty / untracked，哪些远端或权限不可用？ | 避免接管用户或其他 agent 的工作区 |
| 取舍理由 | 本轮为什么选这个小任务，为什么放弃其他候选？ | 让下一轮理解优先级，而不是重新猜测 |
| 可验证结果 | 改了哪些文件，跑了哪些命令，真实输出或断言是什么？ | 区分“写了计划”和“完成了可复核增量” |
| 接力点 | 下一轮第一步看哪里，哪些文件或动作明确不要碰？ | 降低连续 cron 的误操作概率 |

这四段不要求长，但要稳定。尤其是 `当前状态` 必须在修改前记录，而不是事后凭记忆补写；`可验证结果` 必须引用真实命令或人工可复核标准，不能写“应该通过”；`接力点` 要同时包含下一步和禁区。一个合格的交接日志应该让下一轮 Agent 不需要读取完整聊天记录，也能回答：本轮有没有实质变更、变更属于哪个 repo、是否已提交、还有哪些启动前改动不能纳入本轮提交。

反例通常有三类：

1. **成果口径漂移**：日志只写“优化了文档”，没有文件路径、验证命令和提交哈希；下一轮无法判断是否已经入库。
2. **现场污染**：启动时已有 dirty 文件，但日志没有标记归属；后续提交把本轮改动和他人改动混在一起。
3. **授权误读**：外部发布、渠道联系或生产变更缺少人工授权，却被写成“待重试失败”；下一轮可能继续自动重试高风险动作。

因此，无人值守 Agent 的交接日志也应被视为发布系统的一部分：它不只是给人看的日报，而是下一次自动化决策的输入。日志越明确，Agent 越能把时间花在可验证的小步推进上，而不是反复清理上下文债务。

---

## 9.8 本章小结

学习要点：

1. 同步 API、异步任务和人机协作工作流要用不同部署形态。
2. 生产 Agent 必须有状态持久化、任务队列、工具网关和审计日志。
3. 可观测性要覆盖模型、工具、检索、审批、成本和安全拦截。
4. 重试要分类，写操作要幂等，长任务要支持恢复。
5. 事故回放要把线上异常脱敏成可重跑样本，并反向补进第八章评估集和第十章安全门禁。
6. 发布要经过评估、影子流量、灰度和回滚，并把第十章的安全门禁作为独立硬门槛。
7. 发布报告要把第八章的 `run_id`、版本字段、`gate_decision`、`failed_case_ids`、`safe_trace_links` 与第九章补齐的 `release_id` 串成同一条证据链，方便第十章安全门禁、事故复盘和值班回滚直接消费。
8. 无人值守发布还要固定 `readiness.*` 字段契约，用 `status`、`reason`、`next_action`、`push`、人工授权、复核记录和外部 URL 区分 dry-run、blocked、failed 与 published，避免下一轮 Agent 把“未授权停点”误当成发布失败或发布成功。

下一章我们将探讨安全与伦理：如何负责任地开发和运营 AI Agent。

---

*本章结束*
