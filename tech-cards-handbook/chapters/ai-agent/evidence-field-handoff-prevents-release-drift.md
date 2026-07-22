# 证据字段交接要写清生产者和消费者，不要让发布报告各说各话

**问题**：Agent 在评估、发布、安全门禁和事故复盘之间交接证据字段时，怎样避免上一章写 `run_id`、下一章写 `release_id`、最后报告只剩一句“已通过评估”，导致下一轮无法判断哪个字段来自哪里、谁会消费它？

**要点**：

- 每个跨阶段字段都要标明**生产者**和**消费者**：例如评估 runner 生产 `run_id`、`gate_decision`、`failed_case_ids`、`safe_trace_links`，发布流水线补齐 `release_id`，安全门禁和事故复盘消费整条证据链。
- 不要把字段边界写成口号。导读、章节小结、发布报告模板和安全清单里使用同一组字段名，避免“评估报告”“发布报告”“门禁报告”各自发明近义词。
- 字段 handoff 必须保留版本信息：`agent_version`、`prompt_hash`、`model_version`、`tool_schema_version`、`golden_tasks_version` 或等价字段至少能解释行为变化来自哪里。
- `safe_trace_links` 只指向脱敏执行 trace；不要为了调试方便把受限执行 trace、未脱敏工具参数或本机绝对路径塞进公开报告。
- 验证时至少检查两端：生产者示例是否写出字段，消费者小结/清单是否使用同名字段；只检查单个 Markdown 文件容易漏掉跨章节漂移。

**示例**：

```yaml
evidence_handoff:
  produced_by: eval_runner
  consumed_by:
    - release_report
    - safety_gate
    - incident_review
  fields:
    run_id: eval-2026-07-22-001
    release_id: null  # 发布流水线补齐，不由离线评估伪造
    agent_version: candidate-2026.07.22
    prompt_hash: sha256:...
    model_version: gpt-4.1-mini-2026-07
    tool_schema_version: tools-v17
    golden_tasks_version: golden-v12
    gate_decision: warn
    failed_case_ids:
      - refund_requires_approval
    safe_trace_links:
      - artifacts/evals/safe-traces/refund_requires_approval.json
```

对应的轻量检查可以只扫描字段是否在生产端和消费端同时出现：

```python
from pathlib import Path

chapter8 = Path("ai-agent-best-practices/chapters/08-testing-debugging.md").read_text()
chapter9 = Path("ai-agent-best-practices/chapters/09-deployment-monitoring.md").read_text()
chapter10 = Path("ai-agent-best-practices/chapters/10-safety-ethics.md").read_text()

for field in ["run_id", "gate_decision", "failed_case_ids", "safe_trace_links"]:
    assert field in chapter8
    assert field in chapter9
    assert field in chapter10
assert "release_id" in chapter9 and "release_id" in chapter10
```

如果某个字段只在生产端出现，而消费者报告没有承接，要么补消费者模板，要么明确写“本阶段不消费该字段”；不要让下一轮 Agent 自己猜。

**坑**：

- 离线评估报告提前伪造 `release_id`，后来发布流水线又生成另一个 `release_id`，事故复盘时无法定位真实候选版本。
- 第 8 章示例改了 `run_id`，第 9 章小结仍说“沉淀 release_id”，导读和正文边界不一致。
- 安全清单只写“查看评估结果”，没有列出 `gate_decision`、`failed_case_ids` 和 `safe_trace_links`，导致 `warn` / `block` 无法重跑最小失败集。
- 报告里混用 `trace_url`、`debug_link`、`safe_trace` 三套名字，权限 owner 无法判断哪一个可以公开给业务方。
- 最终 summary 只说“字段已对齐”，没有说明扫描了哪些文件、哪些字段、哪些消费者。

**检查**：看到跨阶段证据字段时，先问：字段由谁生产、由谁补齐、由谁消费？导读、正文、小结、模板和清单是否使用同名字段？版本字段是否足以复现候选变更？trace 链接是否只指向脱敏执行 trace？验证是否同时覆盖生产端和消费端？如果任一答案不清楚，本轮先补字段 handoff，再继续扩写流程。