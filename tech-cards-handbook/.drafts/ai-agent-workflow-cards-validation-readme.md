# AI Agent Workflow Cards 验证链路 README

> 用途：把样品包、外联包、Day 1 发送队列、发送记录、反馈跟踪表和 v0.2 修订规则串成一个可执行顺序。这个文件只描述使用方法和证据标准，不记录虚构联系人或用户反馈。

## 当前文件地图

| 文件 | 角色 | 什么时候打开 | 不要拿它做什么 |
|---|---|---|---|
| `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-sample-pack-v0.1.md` | 给目标读者试读的 5 张样卡 | 对方愿意试读后发送 | 不在没有真实反馈前改正文或承诺 |
| `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-outreach-kit.md` | 定位、landing page 文案、私信模板 | 发送前选择对象画像和开场方式 | 不把泛泛点赞当成有效反馈 |
| `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-day1-send-queue.md` | Day 1 发送前队列和模板 | 真正开始第一天外联前 | 不替用户填真实联系人 |
| `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-day1-send-log.md` | Day 1 发送后记录 | 每次发出或收到回复后 | 不只写“已联系”，必须补证据缺口 |
| `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-feedback-tracker.md` | 7 天反馈证据日志和决策表 | 每条回复进入分析前 | 不把 `Record`/`Observe` 直接当修订依据 |
| `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-v0.2-revision-rules.md` | v0.2 是否能改、改哪里、怎么验收 | Day 4 归类或 Day 7 决策时 | 不绕过有效反馈门槛直接扩到 25 张 |
| `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-sample-pack.md` | 早期样品包草稿来源 | 需要追溯原始想法时 | 不直接作为对外发送版本 |

## 推荐执行顺序

### 0. 发送前准备

1. 打开 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-outreach-kit.md`，确认本轮只找已经使用过 coding agent 的目标读者。
2. 打开 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-day1-send-queue.md`，为最多 3 个对象选择对象代号、渠道和模板。
3. 发送前检查私信是否覆盖 5 个反馈问题：
   - 最近一次 agent 失败、跑偏或不可复盘的具体案例；
   - 哪张卡最像这个真实问题；
   - 哪张卡最弱或最不像真实问题；
   - 完整包更适合 Markdown、PDF、Notion 还是网页；
   - 是否愿意留下邮箱、推荐给朋友或看早鸟版本。

### 1. 发送样品包

1. 只有对方愿意试读时，发送 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-sample-pack-v0.1.md`。
2. 不要同时推销完整 25 张包；本轮目标是验证痛点、卡片强弱和交付形式。
3. 发送后立刻更新 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-day1-send-log.md`，至少记录对象代号、模板、是否覆盖 5 问、evidence log 状态。

### 2. 收到回复后先写证据

每条回复先进入 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-feedback-tracker.md` 的「反馈证据日志」，再进入归类区。

| 字段 | 写法 |
|---|---|
| 可观察事实 | 对方原话、具体失败案例、是否留下邮箱、是否要完整包 |
| 推断 | 这条回复可能说明的痛点、定位问题或交付偏好 |
| 置信度 | 低 / 中 / 高；没有具体场景通常是低 |
| 当前分级 | `Record` / `Observe` / `Validate` / `Revise` |
| 下一步验证动作 | 追问、找第二个同类读者、改一张弱卡、或暂不行动 |

分级原则：

- `Record`：礼貌性反馈、收藏、泛泛感兴趣，只保存，不触发动作。
- `Observe`：有方向但证据不足，等待重复信号。
- `Validate`：有具体场景，值得追问或找第二个人验证。
- `Revise`：多条目标读者反馈指向同一问题，可以进入 v0.2 修订。

### 3. Day 4 只归类，不大改

Day 4 的任务是从 feedback tracker 中整理：

- Top 3 真实痛点；
- 最有用卡片排序；
- 最弱卡片或缺失场景；
- 想要的交付形式；
- 推荐、邮箱、早鸟或付费信号。

如果有效反馈少于 2 条，继续外联或收窄对象，不要开始写 25 张完整包。

### 4. Day 7 决策

打开 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-v0.2-revision-rules.md`，按以下门槛做决定：

| 决策 | 条件 | 下一步 |
|---|---|---|
| continue | 至少 5 条有效反馈，且有 2 个以上推荐、邮箱、完整包或早鸟信号 | 写 v0.2 变更记录，只改最影响验证的 1-3 件事 |
| narrow | 反馈集中在单一人群或场景 | 把定位收窄到团队规范、独立开发或 agent 调试等细分方向 |
| stop | 有效反馈少于 2 条，或只有收藏/点赞 | 暂停产品化，把内容回收到书稿或公开文章 |

## 本链路的边界

- 可以改：发送顺序、追问问题、记录字段、v0.2 决策模板、错别字和链接。
- 谨慎改：样品包标题、样卡排序、单张弱卡示例；必须有 `Validate` 或 `Revise` 证据。
- 不要改：凭空扩写到 25 张、虚构用户反馈、写“读者最想要”、直接搭销售页。

## 下一次人工执行时的最小动作

1. 从 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-feedback-tracker.md` 的 10 个对象画像里选 3 个真实对象，但只写用户自己能识别的对象代号，不写隐私信息。
2. 在 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-day1-send-queue.md` 先补齐“真实对象代号选择清单”：为什么是 TA、首句定制点、拒绝后如何归因。
3. 为每个对象确认模板、渠道和预计追问；填不出具体使用场景的人，本轮不发送。
4. 发送前确认样品包问题和私信问题都指向同一套 5 问。
5. 发送后立即更新 `books/tech-cards-handbook/.drafts/ai-agent-workflow-cards-day1-send-log.md`。
6. 收到回复先写「反馈证据日志」，再讨论是否修订。
