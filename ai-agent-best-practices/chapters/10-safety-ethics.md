# AI Agent 最佳实践指南

## 第十章：安全与伦理 —— 负责任地开发 AI Agent

> Agent 的风险来自“能行动”。安全设计要围绕工具、权限、数据和责任边界展开。

---

## 10.1 Agent 的主要安全风险

| 风险 | 典型表现 | 防范重点 |
|------|----------|----------|
| Prompt 注入 | 用户或网页内容诱导 Agent 忽略系统规则 | 指令分层、内容隔离、工具前校验 |
| 工具滥用 | Agent 被诱导发邮件、删数据、转账或执行代码 | 最小权限、风险分级、人工审批 |
| 数据泄露 | 把隐私、密钥、内部文档发给外部模型或用户 | 数据分类、脱敏、访问控制 |
| 越权操作 | 普通用户触发管理员工具 | 用户身份绑定、租户隔离、服务端鉴权 |
| 供应链风险 | 工具、插件、浏览器页面、检索内容不可信 | allowlist、沙箱、依赖审计 |
| 失控循环 | 反复调用工具、耗尽预算或制造垃圾输出 | 最大步数、预算、超时和取消机制 |
| 幻觉执行 | 基于错误事实采取行动 | 关键事实二次验证，高风险动作需确认 |

安全控制不能只写在 Prompt 里。Prompt 是软约束，权限、审计、沙箱和审批才是硬边界。

---

## 10.2 风险分级与权限模型

### 10.2.1 工具风险等级

| 等级 | 示例 | 默认策略 |
|------|------|----------|
| L0 只读低风险 | 查询公开天气、读取公开文档 | 可自动执行，记录日志 |
| L1 只读敏感 | 查询客户资料、内部知识库 | 需要用户身份和访问控制 |
| L2 可逆写操作 | 创建草稿、写入测试环境、更新个人偏好 | 可自动执行或轻量确认 |
| L3 高影响写操作 | 发邮件、改 CRM、提交工单、部署配置 | 需要明确确认和审计 |
| L4 不可逆/高危 | 删除生产数据、转账、法律/医疗/金融建议执行 | 默认禁止或强人工审批 |

### 10.2.2 权限检查应该在服务端

```python
def authorize_tool_call(user, tool, args):
    policy = tool_policy_registry[tool.name]

    if not user.has_permission(policy.required_permission):
        return Decision.block("missing_permission")

    if policy.risk_level >= 3 and not args.get("approval_id"):
        return Decision.require_approval("high_risk_tool")

    if violates_data_boundary(user.tenant_id, args):
        return Decision.block("tenant_boundary_violation")

    return Decision.allow()
```

模型可以建议调用工具，但最终是否执行必须由确定性的权限层决定。

### 10.2.3 高风险工具权限分层与审批策略

不要把“高风险工具需要人工确认”做成一个布尔开关。生产系统更需要把权限拆成**谁能发起、谁能审批、审批什么、多久有效、能否自动降级**。下面是一张可直接落到工具网关或策略服务中的分层表：

| 层级 | 控制点 | 典型规则 | 失败时动作 |
|------|--------|----------|------------|
| 发起权限 | 用户、租户、角色、资源归属 | 普通成员不能发起跨租户写操作；外部协作者不能触发 L3/L4 工具 | 阻断并记录 `missing_permission` |
| 工具权限 | 工具 allowlist、环境、风险等级 | 生产环境只开放已登记 owner、runbook 和回滚方式的工具 | 工具不可见或返回 `tool_not_allowed` |
| 参数权限 | 金额、范围、目标资源、批量大小 | 发邮件人数超过 20、退款金额超过阈值、删除数量超过 1 都升级审批 | 返回 `approval_required` 或拆分任务 |
| 审批权限 | 审批人角色、四眼原则、利益冲突 | 发起人与审批人不能相同；高金额操作需要双审批 | 保持 `awaiting_approval`，不执行工具 |
| 时效权限 | 审批过期、一次性 token、幂等键 | 审批 15 分钟过期；审批只绑定一次 `idempotency_key` | 过期后重新确认，禁止复用旧审批 |
| 运行权限 | 预算、频率、熔断、灰度比例 | 成本超预算或工具失败率异常时自动切只读模式 | 降级到只读或暂停队列 |

审批请求要绑定具体工具和参数快照，而不是只绑定一句自然语言说明。推荐保存：

```json
{
  "approval_id": "appr_123",
  "requester": "user_42",
  "approver_role": "finance_admin",
  "tool": "refund_payment",
  "risk_level": "L4",
  "args_hash": "sha256:...",
  "resource_scope": "tenant_a/payment_987",
  "idempotency_key": "refund_payment_987_once",
  "expires_at": "2026-05-22T10:15:00Z"
}
```

执行前再次校验 `args_hash`、`resource_scope`、`idempotency_key` 和审批有效期，避免 Agent 在审批后偷偷改参数。对 L3/L4 工具，还应优先提供降级路径：生成草稿而不是发送、创建变更请求而不是直接部署、标记待删除而不是立即删除。

---

## 10.3 Prompt 注入防御

Prompt 注入无法靠一句“不要听用户恶意指令”解决。推荐组合防御：

1. **内容隔离**：把用户输入、网页内容、工具返回和系统指令放在不同字段，不拼成一整段不分来源的文本。
2. **不信任外部内容**：网页、邮件、PDF、知识库内容只能作为数据，不能成为系统指令。
3. **工具前校验**：调用工具前检查用户权限、工具风险、参数范围和目标资源。
4. **高风险二次确认**：确认界面展示真实工具名、关键参数、影响范围和回滚方式。
5. **输出过滤**：防止泄露密钥、个人数据、内部 URL 和系统提示。

```python
def prepare_context(user_message, retrieved_docs):
    return {
        "system_instructions": SYSTEM_POLICY,
        "user_message": user_message,
        "untrusted_context": [
            {"source": doc.source, "content": doc.content}
            for doc in retrieved_docs
        ],
    }
```

在 Prompt 中明确 `untrusted_context` 不能覆盖系统规则，但更重要的是工具执行前的服务端检查。

---

## 10.4 数据安全与隐私

### 10.4.1 数据分类

| 数据类型 | 示例 | 处理方式 |
|----------|------|----------|
| 公开数据 | 官网内容、公开价格 | 可用于检索和生成 |
| 内部数据 | 内部文档、会议纪要 | 需要租户和角色访问控制 |
| 个人数据 | 姓名、邮箱、偏好、聊天记录 | 最小化收集、可删除、可导出 |
| 高敏数据 | 密钥、支付信息、身份证、病历 | 默认不进模型上下文，必要时脱敏 |

### 10.4.2 脱敏和保留期限

```python
SENSITIVE_FIELDS = {"api_key", "password", "token", "credit_card", "id_number"}


def redact_sensitive_fields(payload):
    redacted = {}
    for key, value in payload.items():
        if key in SENSITIVE_FIELDS:
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted
```

日志和 trace 也要脱敏。很多泄露不是发生在模型调用本身，而是发生在调试日志、错误报告和第三方观测平台里。

---

## 10.5 人工确认与可解释交接

高风险动作的确认界面至少要展示：

- 要执行的工具。
- 关键参数。
- 影响范围。
- 是否可回滚。
- 发起用户和审批人。
- 审批过期时间。

```python
def build_approval_request(user, tool_name, args, risk_level):
    return {
        "requester": user.id,
        "tool": tool_name,
        "risk_level": risk_level,
        "summary": summarize_action(tool_name, args),
        "args": redact_sensitive_fields(args),
        "expires_in_minutes": 15,
    }
```

不要让用户只看到“是否允许 Agent 继续？”。确认必须具体到动作和参数。

---

## 10.6 审计、问责和事故响应

### 10.6.1 审计日志

```python
def log_audit_event(event_store, event):
    event_store.append({
        "timestamp": utc_now(),
        "trace_id": event.trace_id,
        "user_id": event.user_id,
        "tenant_id": event.tenant_id,
        "tool": event.tool,
        "decision": event.decision,
        "risk_level": event.risk_level,
        "approval_id": event.approval_id,
        "result": event.result,
    })
```

审计日志应 append-only，普通业务逻辑不能随意修改。涉及高风险工具时，要能回答：谁发起、谁批准、调用了什么、参数是什么、结果如何、是否可回滚。

### 10.6.2 事故响应

提前定义事故流程：

1. 暂停相关工具或切换只读模式。
2. 保留 trace、审计日志和模型输入输出。
3. 识别受影响用户、数据和外部系统。
4. 回滚可逆操作。
5. 更新评估集和安全测试，防止复发。
6. 按合规要求通知相关方。

---

## 10.7 伦理边界

Agent 系统要明确哪些任务不应该自动化：

- 重大金融、法律、医疗决策的最终裁定。
- 可能歧视、骚扰、操控或欺骗用户的行为。
- 未经同意收集、推断或传播个人敏感信息。
- 冒充真人、隐藏 AI 身份或伪造授权。
- 无法解释、无法申诉、无法追责的高影响决策。

伦理不是附录，而是产品约束。越是能自动执行任务的 Agent，越需要明确透明度、申诉机制、人工接管和责任归属。

---

## 10.8 发布前安全检查清单

- [ ] 每个工具都有风险等级、权限要求和 owner。
- [ ] 高风险工具默认需要人工确认。
- [ ] 服务端权限检查不会被 Prompt 绕过。
- [ ] 外部网页、邮件、PDF 和检索结果都按不可信内容处理。
- [ ] 日志、trace 和错误报告会脱敏。
- [ ] 有最大步骤数、超时、预算和取消机制。
- [ ] 有租户隔离和数据保留策略。
- [ ] 有红队测试、prompt injection 测试和越权测试。
- [ ] 有事故响应流程和工具熔断开关。
- [ ] 用户知道自己在和 AI 交互，并能请求人工接管。

---

## 10.9 全书总结

《AI Agent 最佳实践指南》覆盖了从概念到生产的关键路径：

1. 理解 Agent 的核心概念和能力边界。
2. 用清晰目标、工具边界和人机协作设计 Agent。
3. 按任务、风险和成本选择模型、框架和基础设施。
4. 从单 Agent 架构逐步演进到状态化、多 Agent 或人机协作工作流。
5. 设计记忆、工具、测试、部署、监控和安全体系。

真正可靠的 Agent 不是“自动做所有事”，而是能在正确的边界内行动，在不确定时停下来，在失败时可追踪、可恢复、可改进。

---

*全书完*
