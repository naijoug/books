# AI Agent Workflow Cards 样品包草案

> 目标：把 `chapters/ai-agent/` 中已有卡片整理成一个可对外展示的最小样品包，用于验证「25 张给程序员的 agent 工作流卡片」这个 offer 是否值得继续产品化。

## 样品包定位

- **目标读者**：已经会用 ChatGPT/Codex/Claude Code 等工具，但经常遇到 agent 跑偏、上下文丢失、工具乱用或长任务无法收尾的程序员。
- **承诺结果**：读完 5 张样卡后，读者能把一个临时 prompt 改造成可复盘、可失败退出、可接力的 agent 工作流。
- **交付形式**：一页 landing page + 5 张免费样卡 + 25 张完整卡片的预售/订阅入口。
- **验证指标**：10 个目标读者中至少 3 个愿意留下邮箱，至少 1 个愿意为完整包付费或明确预约。

## 5 张样卡选择

| 顺序 | 样卡 | 为什么放入样品包 | 对外标题 |
|---|---|---|---|
| 1 | `chapters/ai-agent/agent-model-tool-loop-boundaries.md` | 先建立 agent 的组成边界，避免把模型聊天误认为系统。 | Agent 不是模型，而是模型、工具、循环和边界 |
| 2 | `chapters/ai-agent/tool-descriptions-use-case-input.md` | 工具描述是最容易立刻改进的低成本杠杆。 | 工具描述要写用途和输入，不要只写名字 |
| 3 | `chapters/ai-agent/agent-iteration-limit-failure-exit.md` | 长任务的主要风险是无限循环和无声失败，必须有退出条件。 | 给 Agent 设迭代上限和失败出口 |
| 4 | `chapters/ai-agent/heartbeat-workflow-prevents-drift.md` | 对应 cron/长期任务场景，能体现卡片的实战价值。 | 心跳工作流让长期任务不漂移 |
| 5 | `chapters/ai-agent/memory-is-context-not-source-of-truth.md` | 补上记忆边界，避免把 memory 当数据库或事实来源。 | 记忆用于延续上下文，不是事实唯一来源 |

## Landing page 结构

### Hero

> 25 张 AI Agent Workflow Cards：把一次性 prompt 变成可运行、可复盘、可交接的开发工作流。

副标题：每张卡只解决一个问题：什么时候用、怎么写、哪里会错、如何检查。

### 痛点

- 让 agent 写代码时，经常越改越偏，但不知道哪里开始失控。
- 长任务跑到一半只剩“继续”或“已完成”的空话，没有可接力证据。
- 工具越接越多，模型却更容易选错工具或传错参数。
- memory/context 混在一起，最后既不可验证，也不可复现。

### 免费样品

展示上面 5 张样卡，每张保留固定结构：问题、要点、示例、坑、检查。

### 完整包承诺

完整包计划包含：

1. Agent 边界与失败出口
2. 工具描述与工具选择
3. 记忆、上下文与事实源
4. 心跳、接力与长期任务
5. 人机协作中的验收与回滚

### CTA

- 免费领取 5 张样卡。
- 如果你正在构建 agent 工作流，可预约一次 30 分钟工作流诊断。
- 如果有 10 人以上愿意领取样卡，并出现 1 个付费/预约信号，再继续整理完整 25 张。

## 7 天验证动作

| Day | 动作 | 产物 | 通过信号 |
|---|---|---|---|
| 1 | 把 5 张样卡排版成可分享 Markdown/PDF | 样品包 v0.1 | 内容可在 3 分钟内读完 |
| 2 | 写 landing page 文案 | 一页说明 | 读者能在 10 秒内知道收益 |
| 3 | 私信 5 位经常使用 coding agent 的开发者 | 5 条定制消息 | 至少 2 人愿意看样品 |
| 4 | 发布一条公开帖 | 帖子 + 样品链接 | 至少 5 个点击/收藏/回复 |
| 5 | 收集反馈并标记 objections | 反馈表 | 找到 3 个重复疑问 |
| 6 | 根据反馈改标题、CTA 或卡片顺序 | v0.2 | 价值主张更具体 |
| 7 | 判断继续/收窄/停止 | 决策记录 | 满足邮箱/预约/付费信号之一 |

## 继续写作清单

优先补齐完整包还缺的正式卡片：

- `tool-result-must-be-observable.md`：工具调用结果必须可观察，不能只相信模型口头总结。
- `agent-handoff-needs-state-diff-next-action.md`：接力记录必须包含状态差异和下一步动作。
- `approval-boundaries-for-side-effects.md`：有副作用的动作必须明确审批边界。
- `eval-before-automation.md`：先定义验收样例，再扩大自动化范围。
- `rollback-plan-before-long-running-change.md`：长任务开始前先写回滚计划。

## 暂不做

- 暂不承诺视频课、社群或大型工具平台。
- 暂不把样品包直接做成复杂网页；先用 Markdown/PDF 验证需求。
- 暂不扩展到所有 AI 工具新闻；只聚焦程序员能马上复用的 agent 工作流卡片。
