# AI Agent 系统实践卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 18 张。文件名使用英文 `kebab-case`。

本目录收录 Agent 系统设计、运行边界、工具、记忆、反馈判断、反馈池和心跳工作流等实践卡片；具体 SDK 或语言实现优先放入对应技术栈目录。

## 阅读顺序

### 1. 先确定 Agent 的边界

| 卡片 | 文件 |
|---|---|
| Agent 是模型、工具、循环和边界的组合 | [`agent-model-tool-loop-boundaries.md`](agent-model-tool-loop-boundaries.md) |
| 第一个 Agent 先做研究助手，不要一开始做全能助手 | [`first-agent-research-assistant.md`](first-agent-research-assistant.md) |

### 2. 再打磨工具和上下文

| 卡片 | 文件 |
|---|---|
| 工具描述要写用途和输入，不要只写名字 | [`tool-descriptions-use-case-input.md`](tool-descriptions-use-case-input.md) |
| 工具结果必须可观察，不要只返回“成功” | [`tool-result-must-be-observable.md`](tool-result-must-be-observable.md) |
| 记忆用于延续上下文，不是事实唯一来源 | [`memory-is-context-not-source-of-truth.md`](memory-is-context-not-source-of-truth.md) |

### 3. 建立反馈和运行控制

| 卡片 | 文件 |
|---|---|
| 反馈必须区分事实和推断，不要把感觉当结论 | [`feedback-must-separate-facts-and-inferences.md`](feedback-must-separate-facts-and-inferences.md) |
| 有效反馈才触发修订，不要被每个声音牵着走 | [`validated-feedback-triggers-revision.md`](validated-feedback-triggers-revision.md) |
| 反馈池要把信号留成可执行字段 | [`feedback-pool-keeps-signals-actionable.md`](feedback-pool-keeps-signals-actionable.md) |
| Agent 必须有迭代上限和失败出口 | [`agent-iteration-limit-failure-exit.md`](agent-iteration-limit-failure-exit.md) |
| 心跳工作流让长期任务不漂移 | [`heartbeat-workflow-prevents-drift.md`](heartbeat-workflow-prevents-drift.md) |
| 交接必须写下一步动作，不要只写状态 | [`handoff-must-name-next-action.md`](handoff-must-name-next-action.md) |
| 接力点是信号，不是义务 | [`continuation-is-signal-not-obligation.md`](continuation-is-signal-not-obligation.md) |
| 短节拍任务不要变成重构 | [`short-cadence-tasks-must-not-become-refactors.md`](short-cadence-tasks-must-not-become-refactors.md) |
| 验证先于乐观总结，不要把“看起来完成”当完成 | [`verify-before-optimistic-summary.md`](verify-before-optimistic-summary.md) |
| 未验证项要显式交接，不要藏在顺利总结里 | [`unverified-items-need-explicit-handoff.md`](unverified-items-need-explicit-handoff.md) |
| 最终报告要来自已提交状态，不要来自计划中的状态 | [`report-from-committed-state.md`](report-from-committed-state.md) |

### 4. 最后抽象为助手操作系统

| 卡片 | 文件 |
|---|---|
| AI 助手操作系统先分清身份、用户、工具和心跳 | [`assistant-os-layers.md`](assistant-os-layers.md) |
| 启动层只负责初始化，不应该长期参与运行 | [`bootstrap-is-initialization-only.md`](bootstrap-is-initialization-only.md) |
