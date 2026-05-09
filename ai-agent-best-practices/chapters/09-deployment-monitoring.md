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
日志、指标、Trace、审计日志、离线评估
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

### 9.4.1 日志、指标和 Trace

| 类型 | 必须记录 | 作用 |
|------|----------|------|
| 日志 | 请求 ID、用户/租户、任务状态、错误分类 | 排查单次失败 |
| 指标 | 成功率、延迟、token、工具调用、成本、重试 | 发现趋势和异常 |
| Trace | 模型调用、检索、工具、审批、状态迁移 | 还原完整执行链路 |
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

上线流程建议：

1. 离线评估集通过。
2. 影子流量对比旧版本和新版本。
3. 小比例灰度，只开放低风险任务。
4. 监控成功率、成本、延迟、人工介入和安全拦截。
5. 达到阈值后逐步放量。
6. 保留一键回滚到旧 Prompt、旧模型路由和旧工具版本的能力。

---

## 9.8 本章小结

学习要点：

1. 同步 API、异步任务和人机协作工作流要用不同部署形态。
2. 生产 Agent 必须有状态持久化、任务队列、工具网关和审计日志。
3. 可观测性要覆盖模型、工具、检索、审批、成本和安全拦截。
4. 重试要分类，写操作要幂等，长任务要支持恢复。
5. 发布要经过评估、影子流量、灰度和回滚。

下一章我们将探讨安全与伦理：如何负责任地开发和运营 AI Agent。

---

*本章结束*
