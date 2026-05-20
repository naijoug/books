# AI Agent Workflow Cards 反馈跟踪表

> 用途：配合 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-outreach-kit.md` 执行 7 天验证。这个文件不是宣传文案，而是把 Day 1-3 的外联对象、发送顺序、反馈字段和决策阈值整理成可复制的跟踪表。

## 使用规则

1. 每次只找已经接触过 coding agent 或 AI 编程工具的人；不要为了凑人数找泛泛的“对 AI 感兴趣”的人。
2. 发出样品包前先确认对方愿意看，避免把外联变成垃圾消息。
3. 每条反馈必须先落到证据字段：可观察事实、推断、置信度、当前分级、下一步验证动作；再归入有用卡、无用卡、真实痛点、想要形式、是否愿意推荐、是否愿意为完整包留下邮箱/早鸟意向。
4. 如果对方只说“不错”“有意思”，继续追问一个真实失败案例；没有具体场景就只标记为 `Record`，不计为有效反馈。
5. Day 4 前不要改产品形态，只允许记录和归类；Day 5 再根据前三天反馈重写标题或一张卡。
6. 只有 `Validate` 或 `Revise` 级别的反馈可以进入 v0.2 决策；`Record` 和 `Observe` 只用于观察趋势。

## 10 个优先外联对象画像

| 顺序 | 对象画像 | 推荐渠道 | 为什么找 TA | 首选模板 | 是否已联系 | 样品包是否发出 | 下一步 |
|---:|---|---|---|---|---|---|---|
| 1 | 最近在用 Cursor / Claude Code / Codex 写业务代码的熟人程序员 | 私聊 | 最容易获得具体失败案例和真实工作流细节 | 模板 A | 否 | 否 | 先问是否愿意 10 分钟试读 |
| 2 | 维护团队 AI 编程规范或分享过 agent 使用经验的同事/朋友 | 私聊 | 能判断卡片是否适合团队规范化 | 模板 A / E | 否 | 否 | 请求对“团队可复用”角度反馈 |
| 3 | 在技术群里讨论过 agent 跑偏、上下文丢失的人 | 小社群私聊 | 痛点与样品包高度匹配 | 模板 B | 否 | 否 | 先引用其公开提到的问题 |
| 4 | 写过 AI 编程工具测评或教程的内容作者 | X / 即刻 / 博客评论 / 邮件 | 能判断传播标题和内容包装是否清晰 | 模板 C | 否 | 否 | 请 TA 判断是否有传播价值 |
| 5 | 做内部 DevTools / 平台工程的人 | 私聊 / LinkedIn | 关心权限、日志、验收和失败恢复 | 模板 B / E | 否 | 否 | 询问完整包是否需要团队落地版 |
| 6 | 独立开发者或小团队负责人 | 私聊 / 社群 | 可能愿意为可复用 workflow 付费 | 模板 D | 否 | 否 | 观察是否询问价格或完整包 |
| 7 | 正在做 AI agent 产品或插件的人 | GitHub / X / 邮件 | 能从工具设计角度反馈卡片缺口 | 模板 C | 否 | 否 | 请 TA 挑最弱的一张卡 |
| 8 | 已经购买过 AI 编程课程/资料的人 | 私聊 | 有付费学习习惯，能验证付费意向 | 模板 A / D | 否 | 否 | 问更偏好 Markdown、PDF 还是 Notion |
| 9 | 经常带新人或做技术培训的人 | 私聊 | 能判断卡片是否适合作为教学材料 | 模板 E | 否 | 否 | 询问是否愿意推荐给团队新人 |
| 10 | 对 prompt 合集疲劳、但仍在用 agent 的高级开发者 | 私聊 / 社群 | 能验证“不只是 prompt 合集”的定位 | 模板 D | 否 | 否 | 重点问标题是否区别于 prompt pack |

## 每日发送配额

| 天数 | 目标人数 | 渠道组合 | 今日重点 | 成功标准 | 停止条件 |
|---|---:|---|---|---|---|
| Day 1 | 3 | 熟人私聊 | 验证 10 分钟可读性和最有用卡片 | 至少 2 人愿意收样品包 | 连续 3 人都不愿意看，先改开场白 |
| Day 2 | 3 | 小社群 / 半熟人 | 验证痛点表达是否被理解 | 至少 1 条具体失败案例 | 回复都只说“发来看看”但无后续，收窄对象 |
| Day 3 | 2 | 内容作者 / 工具开发者 | 验证传播价值和产品命名 | 至少 1 条关于定位或标题的建议 | 被认为像普通 prompt 合集，Day 5 重写定位 |
| Day 4 | 0 | 不新增外联 | 归类反馈 | 形成 Top 3 痛点和 Top 2 弱卡 | 有效反馈 < 2 条，则 Day 5 继续外联而不是改产品 |
| Day 5 | 2 | 根据反馈补充 | 测试 v0.2 标题或改写卡 | 新版本比 v0.1 更容易被复述 | 新标题仍无法被复述，继续收窄细分场景 |
| Day 6 | 3 | 跟进已反馈者 | 询问完整包、邮箱或早鸟意向 | 至少 1 个明确 follow-up / 邮箱 / 付费信号 | 全部只愿意免费收藏，改为内容资产路线 |
| Day 7 | 0 | 不新增外联 | 决策 continue / narrow / stop | 得出下一步路径 | 没有具体痛点，不进入 25 张完整包 |

## 反馈记录表

这张表记录外联进度和样品包问题归类；是否触发修订要看下一节的证据分级，而不是只看主观评价。

| 日期 | 对象编号 | 对象类型 | 使用工具 | 联系渠道 | 开场模板 | 是否愿意试读 | 是否发出样品包 | 回复时间 | 最有用卡片 | 最无用卡片 | 真实失败案例 | 想要形式 | 是否愿意推荐 | 付费/早鸟信号 | 下一步 |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | 1 | 熟人程序员 | Cursor / Claude Code / Codex / 其他 | 私聊 | A | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |
| YYYY-MM-DD | 2 | 团队流程负责人 | Cursor / Claude Code / Codex / 其他 | 私聊 | A/E | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |
| YYYY-MM-DD | 3 | 社群开发者 | Cursor / Claude Code / Codex / 其他 | 小社群 | B | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |
| YYYY-MM-DD | 4 | 内容作者 | Cursor / Claude Code / Codex / 其他 | X / 即刻 / 邮件 | C | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |
| YYYY-MM-DD | 5 | 平台工程 / DevTools | Cursor / Claude Code / Codex / 其他 | 私聊 / LinkedIn | B/E | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |
| YYYY-MM-DD | 6 | 独立开发者 | Cursor / Claude Code / Codex / 其他 | 社群 / 私聊 | D | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |
| YYYY-MM-DD | 7 | Agent 工具开发者 | Cursor / Claude Code / Codex / 其他 | GitHub / X / 邮件 | C | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |
| YYYY-MM-DD | 8 | AI 资料付费用户 | Cursor / Claude Code / Codex / 其他 | 私聊 | A/D | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |
| YYYY-MM-DD | 9 | 技术培训 / 带新人者 | Cursor / Claude Code / Codex / 其他 | 私聊 | E | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |
| YYYY-MM-DD | 10 | 高级开发者 | Cursor / Claude Code / Codex / 其他 | 私聊 / 社群 | D | 待定 | 否 |  |  |  |  | Markdown / PDF / Notion / Web | 未问 | 未问 |  |

## 反馈证据日志

每条反馈先写成证据，再决定是否进入归类区。`Record` 只保留，`Observe` 等重复，`Validate` 需要追问或小测试，`Revise` 才能改 v0.2。

| 日期 | 对象编号 | 可观察事实 | 推断 | 置信度 | 当前分级 | 下一步验证动作 |
|---|---:|---|---|---|---|---|
| YYYY-MM-DD | 1 |  |  | 低 / 中 / 高 | Record / Observe / Validate / Revise |  |
| YYYY-MM-DD | 2 |  |  | 低 / 中 / 高 | Record / Observe / Validate / Revise |  |
| YYYY-MM-DD | 3 |  |  | 低 / 中 / 高 | Record / Observe / Validate / Revise |  |

## 反馈归类区

### Top 3 真实痛点

| 排名 | 痛点 | 出现次数 | 代表原话 | 对应样卡 | 是否需要新增卡片 |
|---:|---|---:|---|---|---|
| 1 |  | 0 |  |  | 否 |
| 2 |  | 0 |  |  | 否 |
| 3 |  | 0 |  |  | 否 |

### 最有用卡片排序

| 卡片 | 提及次数 | 为什么有用 | 下一步 |
|---|---:|---|---|
| `agent-model-tool-loop-boundaries.md` | 0 |  | 保留 / 重写 / 扩展示例 |
| `tool-descriptions-use-case-input.md` | 0 |  | 保留 / 重写 / 扩展示例 |
| `agent-iteration-limit-failure-exit.md` | 0 |  | 保留 / 重写 / 扩展示例 |
| `memory-is-context-not-source-of-truth.md` | 0 |  | 保留 / 重写 / 扩展示例 |
| `heartbeat-workflow-prevents-drift.md` | 0 |  | 保留 / 重写 / 扩展示例 |

### 最弱卡片排序

| 卡片 | 被质疑次数 | 问题类型 | 修订方向 |
|---|---:|---|---|
| `agent-model-tool-loop-boundaries.md` | 0 | 太基础 / 不够具体 / 缺例子 / 不解决痛点 |  |
| `tool-descriptions-use-case-input.md` | 0 | 太基础 / 不够具体 / 缺例子 / 不解决痛点 |  |
| `agent-iteration-limit-failure-exit.md` | 0 | 太基础 / 不够具体 / 缺例子 / 不解决痛点 |  |
| `memory-is-context-not-source-of-truth.md` | 0 | 太基础 / 不够具体 / 缺例子 / 不解决痛点 |  |
| `heartbeat-workflow-prevents-drift.md` | 0 | 太基础 / 不够具体 / 缺例子 / 不解决痛点 |  |

## Day 7 决策模板

```text
结论：continue / narrow / stop

有效外联人数：{valid_outreach_count}
有效反馈数：{specific_feedback_count}
Validate / Revise 级别证据数：{decision_grade_count}
最强痛点：{top_pain}
最强卡片：{top_card}
最弱卡片：{weakest_card}
推荐形式：Markdown / PDF / Notion / Web
付费/早鸟信号：{payment_signal}

下一步：
- 如果 continue：写 25 张完整包的大纲，并先补 3 张最被要求的卡。
- 如果 narrow：把完整包改成面向 {segment} 的 10 张场景卡。
- 如果 stop：把样品包转成免费 blog / docs 内容，不继续产品化。
```
