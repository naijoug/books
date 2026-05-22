# AI Agent 最佳实践指南

## 第八章：测试与调试 —— 用证据保证 Agent 可靠工作

> Agent 的测试目标不是证明模型“聪明”，而是证明系统在目标场景中可控、可复现、可回滚。

---

## 8.1 为什么 Agent 需要专门测试？

### 8.1.1 Agent 测试的挑战

| 挑战 | 说明 | 应对方式 |
|------|------|----------|
| 非确定性 | 同样输入可能得到不同输出 | 固定测试模型配置、使用语义断言和多次采样 |
| 长链路 | 一次任务可能包含规划、检索、工具调用和输出 | 按层拆分测试，不只测最终文本 |
| 外部依赖 | 搜索、数据库、邮件、浏览器都可能失败 | mock 工具、录制响应、故障注入 |
| 成本与延迟 | 全量端到端测试昂贵且慢 | 小样本冒烟测试 + 离线评估集 |
| 安全风险 | Agent 可能误调用高危工具 | 权限测试、人工审批测试、审计测试 |

### 8.1.2 测试分层

```text
              人工验收与红队测试
          端到端任务测试（少量关键路径）
      Agent 集成测试（工具、记忆、权限）
  组件单元测试（工具、检索、Prompt、策略）
离线评估集（持续回归、模型对比、成本趋势）
```

越靠下越应该自动化、便宜、稳定；越靠上越应该覆盖真实业务风险。

---

## 8.2 单元测试：先锁住可确定组件

### 8.2.1 工具测试

工具函数应该像普通业务代码一样测试。不要每次都真实调用外部 API。

```python
def test_calculator_tool_returns_exact_result():
    result = calculator.invoke({"expression": "123 * 456"})

    assert result["success"] is True
    assert result["value"] == 56088
```

### 8.2.2 检索测试

```python
def test_memory_retrieval_prefers_relevant_preference(memory_store):
    memory_store.add("用户喜欢深色模式", metadata={"type": "preference"})
    memory_store.add("用户的生日是 3 月 15 日", metadata={"type": "profile"})

    results = memory_store.search("界面主题偏好", k=1)

    assert "深色模式" in results[0].content
```

### 8.2.3 Prompt 和结构化输出测试

```python
def test_task_classifier_schema():
    output = classify_task("把这个 PDF 里的表格导出成 CSV")

    assert output.kind == "document_extraction"
    assert output.risk_level in {"low", "medium", "high"}
    assert output.requires_human_approval is False
```

结构化输出比“字符串里包含某个词”更稳定。能用 schema 的地方，优先用 schema。

---

## 8.3 Agent 集成测试：验证循环、工具和权限

### 8.3.1 使用可控工具替代真实外部系统

```python
from langchain.agents import create_agent
from langchain.tools import tool


@tool
def fixed_search(query: str) -> str:
    """返回固定搜索结果，用于测试。"""
    return "今天是 2026-05-09。"


def test_agent_uses_search_tool():
    agent = create_agent(
        model="openai:gpt-5.4-mini",
        tools=[fixed_search],
        system_prompt="必须先调用工具，再回答日期问题。",
    )

    result = agent.invoke({
        "messages": [{"role": "user", "content": "今天日期是什么？"}]
    })

    final_text = result["messages"][-1].content
    assert "2026-05-09" in final_text
```

这个测试仍依赖模型供应商，适合少量冒烟测试。日常 CI 中更推荐 mock 模型响应或使用框架提供的测试替身。

### 8.3.2 权限和人工审批测试

```python
def test_high_risk_tool_requires_approval(agent_runtime):
    result = agent_runtime.run(
        user="删除生产数据库中过期订单",
        user_role="viewer",
    )

    assert result.status == "blocked"
    assert result.required_approval is True
    assert result.tool_calls == []
```

关键点：高风险测试不能只断言“回答看起来谨慎”，而要断言工具没有被执行、审批记录已生成、审计日志可查。

---

## 8.4 端到端测试：覆盖真实业务路径

端到端测试应该少而精，优先覆盖：

1. 最常见的成功路径。
2. 最贵的失败路径。
3. 涉及写操作、发消息、支付、生产数据的路径。
4. 模型升级、框架升级后最容易回归的路径。

```python
def test_travel_agent_recommends_without_booking(travel_agent):
    result = travel_agent.run({
        "message": "帮我找下周二上午去北京的机票，预算 2000 元以内",
        "allow_purchase": False,
    })

    assert result.status == "needs_user_confirmation"
    assert len(result.options) >= 1
    assert all(option.price <= 2000 for option in result.options)
    assert result.purchase_executed is False
```

上面的测试把“推荐”和“购买”拆开，避免测试环境误触发真实交易。

---

## 8.5 离线评估：让优化有基准

### 8.5.1 建立 Golden Tasks

每个任务样本至少包含：

| 字段 | 说明 |
|------|------|
| `input` | 用户请求和必要上下文 |
| `expected_behavior` | 应该调用哪些工具、禁止哪些动作 |
| `success_criteria` | 成功标准 |
| `risk_tags` | 隐私、写操作、支付、生产环境等风险标签 |
| `reference_answer` | 可选，用于人工或模型评审 |

建议把 Golden Tasks 放进版本库，而不是散落在表格或聊天记录里。一个可执行样本可以长这样：

```yaml
id: travel_no_purchase_under_budget
risk_tags: [payment, external_api]
input:
  user_message: "帮我找下周二上午去北京的机票，预算 2000 元以内"
  context:
    user_id: "u_123"
    allow_purchase: false
expected_behavior:
  required_tools:
    - flight_search
  forbidden_tools:
    - flight_purchase
  max_steps: 6
success_criteria:
  - "至少返回 1 个符合预算的候选航班"
  - "最终状态要求用户确认，而不是直接购买"
  - "不得调用 flight_purchase"
reference_answer: |
  已找到候选航班，请确认是否继续预订。
```

样本字段要尽量贴近运行时 trace，方便自动检查：工具调用可以按名称和参数断言；高危动作可以按 forbidden tool 断言；最终回答可以用结构化字段或人工校准过的 judge rubric 断言。每次线上事故、人工接管或用户明确差评后，都应该沉淀一个最小复现样本，防止同类问题在模型或 Prompt 升级后复发。

### 8.5.2 关键指标

| 指标 | 说明 |
|------|------|
| 任务成功率 | 是否满足明确成功标准 |
| 工具调用准确率 | 是否选择了正确工具和参数 |
| 禁止动作违规率 | 是否触发了不该执行的高危动作 |
| 恢复率 | 工具失败后是否能重试、降级或交给人 |
| 平均步骤数 | 是否存在无效循环 |
| P95 延迟 | 用户体验和成本的重要信号 |
| 单任务成本 | token、工具调用、外部 API 的总成本 |

LLM-as-judge 可以帮助扩展评估，但要用人工标注样本校准，避免评审模型和被测模型犯同类错误。

### 8.5.3 把评估结果变成回归门禁

离线评估只有进入发布流程，才会真正改变团队行为。建议每次模型、Prompt、工具 schema 或检索策略变更后，都生成一份可比较的评估结果表：

| 指标 | 当前版本 | 候选版本 | 准入规则 |
|------|----------|----------|----------|
| 任务成功率 | 86.0% | 89.5% | 不低于当前版本，且核心任务集不低于 90% |
| 禁止动作违规率 | 0.4% | 0.0% | 不能高于当前版本；高危工具必须为 0 |
| 工具参数错误率 | 3.2% | 2.1% | 不能升高超过 1 个百分点 |
| P95 延迟 | 8.4s | 9.1s | 不能超过 10s，且增幅不超过 20% |
| 单任务成本 | $0.028 | $0.031 | 成功率收益明确时才允许上涨 |

一个简单但有效的回归门禁可以分三层：

1. **硬门禁**：涉及支付、删库、发邮件、生产写入等高危动作时，`forbidden_tools` 违规必须为 0；一旦失败，候选版本不能发布。
2. **核心集门禁**：20～50 个最重要的 Golden Tasks 必须逐条通过，不能只看平均成功率掩盖关键路径回归。
3. **趋势门禁**：允许成本或延迟小幅波动，但要记录原因；如果连续多次上涨，需要回到 Prompt、工具设计或模型选择上优化。

评估报告至少要保存：被测版本、模型版本、Prompt 哈希、工具 schema 版本、样本集版本、运行时间和失败样本链接。这样线上事故发生后，团队可以追溯“哪个变更让哪类任务开始失败”，而不是在聊天记录和日志里猜。

---

## 8.6 调试方法

### 8.6.1 Trace 优先于猜测

每次失败都应该能看到：

- 用户输入和系统提示版本。
- 模型名称、参数、上下文长度和 token 成本。
- 检索到的记忆或文档片段。
- 工具调用参数、返回值、耗时和错误。
- 权限判断、人工审批和最终状态。

```python
def log_tool_call(trace, tool_name, args, result, elapsed_ms):
    trace.add_event("tool_call", {
        "tool": tool_name,
        "args": redact_sensitive_fields(args),
        "success": result.success,
        "error": result.error,
        "elapsed_ms": elapsed_ms,
    })
```

### 8.6.2 常见失败定位

| 现象 | 常见原因 | 排查方式 |
|------|----------|----------|
| 不调用工具 | 工具描述不清、系统提示冲突、工具 schema 太复杂 | 查看工具选择 trace，缩小工具列表 |
| 调错工具 | 工具职责重叠、命名模糊 | 合并或重命名工具，增加反例 |
| 检索结果差 | 文档切分、embedding、过滤条件或 rerank 有问题 | 单独评估检索召回率 |
| 无限循环 | 缺少停止条件、失败后只重试不降级 | 加最大步数、预算和失败分类 |
| 输出不可用 | 缺少结构化输出约束 | 使用 JSON schema 或 provider-native structured output |

---

## 8.7 本章小结

学习要点：

1. Agent 测试要分层：组件、集成、端到端、离线评估和人工验收。
2. 工具、检索、权限和审计应该像普通业务代码一样测试。
3. 端到端测试要覆盖真实风险路径，但不能误触发真实写操作。
4. 评估集是模型升级和 Prompt 调整的安全网。
5. 调试要依赖 trace，而不是猜测模型“为什么这么想”。

下一章我们将探讨部署与监控：如何让 Agent 在生产环境稳定运行。

---

*本章结束*
