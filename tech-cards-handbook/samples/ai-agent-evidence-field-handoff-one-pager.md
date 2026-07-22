# AI Agent 证据字段 handoff 一页纸

> 用途：当评估报告、发布报告、安全门禁和事故复盘之间开始混用 `run_id`、`release_id`、`trace_url`、`safe_trace_links` 等字段时，用这一页先固定生产者、补齐者和消费者，再改模板或章节正文。

## 1. 先画字段链，不要先改文案

```text
候选变更：<agent / prompt / tool schema / model route>
生产阶段：<eval runner / CI / manual review>
补齐阶段：<release pipeline / deploy job / safety gate>
消费阶段：<release report / safety gate / on-call / incident review>
本轮目标：<补生产端 / 补消费端 / 统一字段名 / 明确不消费>
```

如果这五行填不出来，本轮不要继续扩写“已通过评估”这类总结句；先把字段边界补清楚。

## 2. 最小字段表

| 字段 | 生产者 | 补齐者 | 消费者 | 检查问题 |
|---|---|---|---|---|
| `run_id` | eval runner | 无 | 发布报告、安全门禁、事故复盘 | 能定位是哪次离线评估吗？ |
| `release_id` | 无 | 发布流水线 | 安全门禁、值班回滚、事故复盘 | 是否只在发布阶段生成，避免离线评估伪造？ |
| `agent_version` / `prompt_hash` / `model_version` | 代码、Prompt 仓库、模型路由 | 发布流水线确认 | 发布 owner、安全 owner | 能复现候选行为变化来自哪一层吗？ |
| `gate_decision` | eval runner 或门禁执行器 | 安全门禁可降级 | 发布报告、灰度策略 | `pass` / `warn` / `block` 是否对应可执行动作？ |
| `failed_case_ids` | eval runner | 无 | 调试、复跑、安全门禁 | 是否能重跑最小失败集？ |
| `safe_trace_links` | 脱敏 trace 生成器 | 发布流水线引用 | 调试、安全 owner、事故复盘 | 是否只指向脱敏 trace，而不是本机路径或原始敏感日志？ |
| `audit_event_ids` | 工具网关 / 审计系统 | 发布流水线引用 | 安全门禁、合规复盘 | 是否能核对权限拒绝、审批、熔断和人工接管真实发生？ |

## 3. 可复制检查片段

```python
from pathlib import Path

producer = Path("ai-agent-best-practices/chapters/08-testing-debugging.md").read_text()
release = Path("ai-agent-best-practices/chapters/09-deployment-monitoring.md").read_text()
safety = Path("ai-agent-best-practices/chapters/10-safety-ethics.md").read_text()

producer_fields = [
    "run_id",
    "gate_decision",
    "failed_case_ids",
    "safe_trace_links",
    "audit_event_ids",
]
for field in producer_fields:
    assert field in producer, f"producer missing {field}"
    assert field in release, f"release report does not consume {field}"
    assert field in safety, f"safety gate does not consume {field}"

for field in ["release_id", "model_version", "prompt_hash"]:
    assert field in release, f"release report missing {field}"
    assert field in safety, f"safety gate missing {field}"

for text in [producer, release, safety]:
    assert "HOME_DIRECTORY/" not in text
```

这段检查只证明字段名没有漂移，不证明流程真的自动化；如果要验证真实流水线，还要跑评估 runner、发布 job 或门禁脚本。

## 4. Notebook 记录句式

```text
- 实际推进：本轮围绕 <字段链> 做 path-limited 修正；明确 <生产者> 产出 <字段>，<补齐者> 补齐 <字段>，<消费者> 读取同名字段。
- 验证方式：运行 <检查命令>，确认生产端、发布报告和安全门禁都包含 <字段列表>，且不含本机绝对路径；未验证真实 CI/job 执行。
- 后续接力：下一次第一步是 <运行真实 runner / 检查模板入口 / 补消费者清单>，验证目标是 <字段可重跑 / 报告可消费 / 回滚可定位>。
```

## 5. 收尾检查

- 是否写清每个字段的生产者、补齐者和消费者？
- `run_id` 与 `release_id` 是否没有互相伪造？
- `gate_decision` 是否能转成 `pass` / `warn` / `block` 的动作，而不是一句主观信心？
- `safe_trace_links` 是否只指向脱敏 trace，且没有本机绝对路径？
- 验证记录是否区分“字段名一致”与“真实流水线已跑通”？
- 如果某阶段不消费某字段，是否显式写了“不消费”而不是留空让下一轮猜？

相关卡片：`books/tech-cards-handbook/chapters/ai-agent/evidence-field-handoff-prevents-release-drift.md`。
