# 工具结果必须可观察，不要只返回“成功”

**问题**：Agent 调用工具后，为什么仍然会重复操作、误判状态，或把失败当成成功？

**要点**：

- 工具返回值要包含可观察事实，而不只是 `ok`、`done`、`success`。
- 返回结果应说明关键输出、影响范围、下一步可用的证据，以及必要的错误原因。
- 如果工具有副作用，返回值要让 Agent 能判断“是否真的发生了变化”。

**示例**：

```json
{
  "status": "updated",
  "path": "docs/agent-tools.md",
  "changed_lines": 18,
  "summary": "Added observable tool-result checklist",
  "next_check": "Run markdown lint or read back the edited section"
}
```

**坑**：只返回 `success: true` 会让 Agent 失去后续判断依据；当写入路径错误、命中空结果或部分失败时，模型可能继续基于错误状态推理。

**检查**：遮住工具实现，只看返回值，下一轮 Agent 是否能回答三个问题：发生了什么、证据在哪里、下一步该验证什么？如果不能，返回值还不够可观察。
