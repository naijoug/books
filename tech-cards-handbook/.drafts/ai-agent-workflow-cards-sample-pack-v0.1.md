# AI Agent Workflow Cards 免费样品包 v0.1

> 这是一份可直接分享给目标读者的 Markdown 样品包，用来验证「25 张给程序员的 AI Agent Workflow Cards」是否值得继续产品化。来源草案：`books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-sample-pack.md`。

## 一句话说明

把一次性 prompt 变成可运行、可复盘、可接力的 agent 工作流。

适合你，如果你已经会用 ChatGPT、Codex、Claude Code 或类似 coding agent，但经常遇到这些问题：

- agent 一开始很聪明，跑久了却开始偏离目标；
- 工具很多，但模型经常选错工具、传错输入或只口头总结结果；
- 长任务失败时只剩“继续”“已完成”之类的空话，没有可复盘证据；
- memory、上下文、项目文件和真实状态混在一起，导致重复工作或误判完成。

这份样品包先给出 5 张卡。每张卡只解决一个问题：什么时候用、怎么写、哪里会错、如何检查。

## 读法

每张卡按同一结构阅读：

1. **问题**：这张卡避免什么失败模式。
2. **要点**：设计或使用 agent 时必须写清的边界。
3. **示例**：最小可抄走的表达。
4. **坑**：常见误用。
5. **检查**：读完后立刻能做的验收动作。

建议用法：挑一个你最近让 agent 做过的任务，把下面 5 张卡逐张对照，补上缺失的边界和检查点。

---

## 卡 1：Agent 不是模型，而是模型、工具、循环和边界

来源：`books/tech-cards-handbook/chapters/ai-agent/agent-model-tool-loop-boundaries.md`

**问题**：怎么判断一个程序是不是 agent，而不只是一次普通模型调用？

**要点**：

- Agent 至少包含模型、工具、决策循环和停止条件。
- 模型负责判断下一步，工具负责改变或查询外部世界。
- 停止条件和权限边界决定它是否可控。

**示例**：

```text
用户目标 -> 模型判断 -> 选择工具 -> 读取结果 -> 再判断 -> 输出或停止
```

**坑**：只接上工具但没有迭代上限、错误处理和权限边界，agent 很容易从“自动化”变成“失控重试”。

**检查**：为每个 agent 写清楚三件事：它能调用什么？最多运行多久？什么时候必须停下来交还控制权？

**可复制改写**：

```text
这个 agent 的目标：{goal}
允许调用的工具：{tools}
禁止做的动作：{forbidden_actions}
最多运行：{max_iterations} 轮或 {max_minutes} 分钟
必须停止并汇报的情况：{handoff_conditions}
```

---

## 卡 2：工具描述要写用途和输入，不要只写名字

来源：`books/tech-cards-handbook/chapters/ai-agent/tool-descriptions-use-case-input.md`

**问题**：为什么 agent 明明有工具，却经常选错或不会用？

**要点**：

- 工具名称应表达动作，例如 `SearchWeb`、`SaveNote`。
- 工具描述要说明适用场景和输入格式。
- 工具返回值要短而结构化，方便模型继续推理。

**示例**：

```python
Tool(
    name="SaveNote",
    func=save_note,
    description="保存研究笔记到 Markdown 文件。输入必须是完整 Markdown 正文。",
)
```

**坑**：工具描述写成“很好用的保存工具”没有可执行信息；模型不知道什么时候调用，也不知道该传什么。

**检查**：遮住工具实现，只看名称和描述，人类是否也能正确使用？如果不能，模型通常也不能。

**可复制改写**：

```text
工具名：{VerbNoun}
用途：当 agent 需要 {use_case} 时调用。
输入：{input_schema_or_plain_language_contract}
返回：{short_structured_result}
不要用于：{out_of_scope_case}
```

---

## 卡 3：给 Agent 设迭代上限和失败出口

来源：`books/tech-cards-handbook/chapters/ai-agent/agent-iteration-limit-failure-exit.md`

**问题**：如何避免 agent 卡在解析错误、工具失败或目标不清的循环里？

**要点**：

- 设置最大迭代次数和最大运行时间。
- 工具失败要返回可读错误，而不是让异常完全吞没上下文。
- 连续失败时应总结当前状态并停止，而不是无限重试。

**示例**：

```text
max_iterations: 5
on_tool_error: 记录工具名、输入、错误摘要
stop_after: 连续 2 次同类失败
```

**坑**：把 `handle_parsing_errors` 当成万能兜底，只会隐藏 prompt、工具 schema 或模型输出格式的问题。

**检查**：故意让一个工具失败，agent 是否会给出清楚的失败原因和下一步，而不是继续空转？

**可复制改写**：

```text
失败出口：
- 连续 {n} 次同类工具失败：停止，输出工具名、输入摘要、错误摘要、建议修复。
- 连续 {n} 次无法判断下一步：停止，列出缺失信息，不再猜测。
- 达到 {max_iterations} 轮：停止，输出已完成、未完成、下一步。
```

---

## 卡 4：心跳工作流让长期任务不漂移

来源：`books/tech-cards-handbook/chapters/ai-agent/heartbeat-workflow-prevents-drift.md`

**问题**：长任务运行一段时间后，如何避免忘记目标、只产出噪音或停在半路？

**要点**：

- 心跳不是激励语，而是状态闭环。
- 最小流程是：读取状态 -> 生成提醒 -> 执行自检 -> 写回进展。
- 每次心跳都要留下下一轮能读取的证据。

**示例**：

```text
心跳检查：{task_name}
上次状态：{last_progress}
请用 3 行更新：
1. 已完成：
2. 阻碍：
3. 下一步：
```

**坑**：只发送“继续努力”这类提醒，很快会变成噪音；没有写回动作，就不能形成系统。

**检查**：下一次运行能否从心跳记录里直接知道当前阻碍和下一步？能，才算闭环。

**可复制改写**：

```text
每次心跳必须更新：
- 当前目标是否仍然正确：{yes_no_and_reason}
- 本轮实际完成：{observable_change}
- 当前阻碍：{blocker_or_none}
- 下一轮第一步：{next_action}
- 可复核证据：{file_path_commit_test_log_or_link}
```

---

## 卡 5：记忆用于延续上下文，不是事实唯一来源

来源：`books/tech-cards-handbook/chapters/ai-agent/memory-is-context-not-source-of-truth.md`

**问题**：agent 有了记忆后，为什么仍然需要读取项目文件和当前状态？

**要点**：

- 记忆会过期，项目文件和运行状态更接近事实现场。
- 记忆适合保存偏好、长期背景和上次进展。
- 关键判断前应回读权威来源，例如 README、索引、测试输出或数据库记录。

**示例**：

```text
USER.md：用户偏好和长期背景
README.md：当前项目状态
progress.json：最近一次自动运行进度
```

**坑**：把“上次记得的进度”当成真实进度，会导致重复工作或错误声明完成。

**检查**：凡是会影响写入、删除、发布或完成声明的信息，都应该有当前来源，而不是只来自记忆。

**可复制改写**：

```text
做关键判断前，先列出事实来源：
- 用户长期偏好：{memory_or_profile_path}
- 项目当前结构：{readme_or_index_path}
- 本轮真实状态：{git_status_test_log_runtime_state}
- 完成证据：{observable_output}
如果没有当前来源，只能说“假设”，不能说“已确认”。
```

---

## 3 分钟自检清单

把你正在使用的 agent 工作流拿出来，逐项回答：

- [ ] 它的模型、工具、循环和停止条件是否写清楚了？
- [ ] 每个工具描述是否包含用途、输入和返回格式？
- [ ] 是否有最大迭代次数、最大运行时间和连续失败出口？
- [ ] 长任务是否会写回可复核心跳，而不是只说“继续”？
- [ ] 完成声明是否来自当前文件、测试、运行状态或日志，而不是只来自记忆？

如果有 2 项以上答不上来，先不要加更多工具；先补边界和检查点。

## 完整包计划

完整包暂定 25 张，覆盖：

1. Agent 边界与失败出口；
2. 工具描述、工具选择和工具结果可观察性；
3. 记忆、上下文与事实源；
4. 心跳、接力与长期任务；
5. 人机协作中的验收、审批和回滚。

如果这份样品包对你有用，下一步会把缺口卡片补齐成正式版本，例如：

- `books/tech-cards-handbook/chapters/ai-agent/tool-result-must-be-observable.md`
- `books/tech-cards-handbook/chapters/ai-agent/agent-handoff-needs-state-diff-next-action.md`
- `books/tech-cards-handbook/chapters/ai-agent/approval-boundaries-for-side-effects.md`
- `books/tech-cards-handbook/chapters/ai-agent/eval-before-automation.md`
- `books/tech-cards-handbook/chapters/ai-agent/rollback-plan-before-long-running-change.md`

## 反馈问题

为了决定是否继续做完整包，只需要收集 4 个反馈：

1. 哪一张卡最像你最近遇到的问题？
2. 哪一张卡你读完仍然不知道怎么用？
3. 你更想要 Markdown、PDF、Notion 模板，还是可导入 agent 配置的模板？
4. 如果完整包解决 25 个类似失败模式，你愿意付费、预约诊断，还是只想继续看免费内容？
