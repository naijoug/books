# AI Agent External Publish Authorization One-Pager

用途：当 agent 已经准备好外部发布文案、付费 offer 或公开案例，但当前会话没有明确授权时，用这页纸把“能不能发、发到哪里、谁来接回复、观察多久”压缩成一张可交接表。它配套 [`../chapters/ai-agent/external-publish-needs-authorization.md`](../chapters/ai-agent/external-publish-needs-authorization.md)，重点不是让 agent 更快外发，而是防止无人值守任务把本地草稿误当成发布许可。

相关运行材料可参考 `makemoney/docs/offer-authorization-request-brief.md`、`docs/documents/trending/ai/single-channel-offer-publish-preflight.md` 和 `skills/skills/manual/business/single-channel-offer-publish/SKILL.md`。这里故意使用路径文本而不是书内链接，因为这些材料位于其他仓库，不属于本书链接校验范围。

## 30 秒入口判断

| 看到的信号 | 默认决策 | 立即写下的缺口 |
|---|---|---|
| 有 offer 文案，但没有渠道授权 | `Wait for authorization` | `Channel authorization` |
| 有渠道名，但没有账号/身份 | `Wait for authorization` | `Account / identity` |
| 有账号，但没有回复入口 | `Wait for authorization` | `Contact path` |
| 有发布许可，但没有观察窗口 | `Narrow` | `Observation window` |
| 有完整授权包，且只发一个渠道 | `Publish` | `Evidence log` |
| agent 想同时发多个渠道 | `Narrow` | `Single-channel scope` |

默认规则：缺 `Channel authorization`、账号/身份、`Contact path` 或 `Observation window` 任一项，都不要外发；只允许把阻塞压缩成授权请求或单渠道 preflight。

## Authorization packet

```text
Offer / artifact:
Channel authorization:
Account / identity:
Contact path:
Observation window:
Allowed publish copy:
Do-not-touch fields:
```

填写规则：

- `Offer / artifact` 写具体文件或文案名称，不写“发一下那个服务”。
- `Channel authorization` 必须说明渠道和许可来源，例如“用户确认可发到 X 账号”。
- `Contact path` 必须能接收回复或线索；没有联系路径时，不要发布只能点赞的内容。
- `Observation window` 写开始/结束时间，避免发布后无人记录反馈。
- `Do-not-touch fields` 写价格、承诺、截图、客户名、联系方式等不能由 agent 自行改动的字段。

## 单渠道发布前最后检查

```text
Decision: Publish / Wait for authorization / Narrow / Switch
Chosen channel:
Why this channel first:
What will be posted exactly:
Reply handling owner:
Evidence log path:
Next safe command:
```

发布前必须能回答：

1. 这次是不是只发一个渠道？
2. 文案是否与授权包逐字一致，未新增价格、承诺或联系方式？
3. 回复由谁处理，在哪里记录？
4. 如果 24 小时内没有有效回复，下一步是继续、收窄、停止还是切换？

## 阻塞时的最小交接句

```text
Decision: Wait for authorization. Missing: Channel authorization / Account / Contact path / Observation window. Do not publish. Next safe command: ask user to fill the authorization packet, then run the single-channel preflight and record the evidence log path.
```

## 常见反模式

- 用“已有草稿”替代 `Channel authorization`。
- 用 agent 自己推测的邮箱、社媒账号或私信入口替代 `Contact path`。
- 为了显得有进展，继续扩 offer 功能、价格页或交付模板。
- 没有观察窗口就发布，导致后续无法判断 `Continue / Narrow / Stop / Switch`。
- 发布前临时改价格、承诺、交付范围或客户案例边界。

## 验收标准

一轮外部发布动作只有在下面条件同时满足时才算可执行：

- 授权包四项完整：`Channel authorization`、账号/身份、`Contact path`、`Observation window`。
- 决策表写出 `Publish`，并说明为什么不是 `Wait for authorization`。
- `Next safe command` 是具体发布或记录命令，不是“继续完善”。
- 发布后立刻记录 URL、时间、联系路径、观察窗口和下一次复盘点。

否则本页的交付物就是一条可复查的阻塞说明，而不是发布行为。
