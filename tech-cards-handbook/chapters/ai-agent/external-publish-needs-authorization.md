# 外部发布先要授权，不要把草稿当成发布许可

## 问题

无人值守 Agent 经常能把 offer、教程、发布帖和回复模板准备到“看起来可以发”的程度，但外部发布不是本地写作：它会使用用户账号、联系方式、渠道信誉和后续响应承诺。没有明确授权时，继续打磨交付物很容易变成两种漂移：一是擅自外发，二是用更多文档掩盖真正阻塞点。

这张卡解决的问题是：当 Agent 已经有发布素材，但缺少渠道、账号、联系方式或观察窗口时，应该怎样默认停止外发，并把阻塞压缩成可回答的授权请求。

## 要点

1. **发布授权不是“内容已准备好”**：本地文件、草稿、首帖模板、价格页和 preflight 都只能证明素材存在，不能证明用户允许使用某个渠道发出。
2. **五个字段缺一不可**：`Offer / 实验`、`Channel / account`、`Contact path`、`Target audience / authorized targets`、`Observation window`。少一个字段，默认结论就是 `Wait for authorization`。
3. **无人值守默认不外发**：cron、批处理或夜间 Agent 无法现场处理回复、删帖、澄清误解和隐私边界，除非用户提前给出明确窗口和处理规则。
4. **阻塞期间不要继续堆交付功能**：如果 gate 已经卡在授权层，继续补 FAQ、样例包或自动化脚本通常不能提高成交概率；更好的下一步是把授权请求写成五个问题。
5. **只发布一个渠道**：获得授权后先执行单渠道 preflight，记录 URL、时间、首个反馈和 24 小时观察结果；不要因为终于获批就同时跨多个渠道扩散。

## 示例

```text
Publish gate
- Offer / 实验: LLM 成本与可观测性快速体检
- Channel / account: missing
- Contact path: missing
- Target audience / authorized targets: missing
- Observation window: missing
- Decision: Wait for authorization

Authorization request to user
1. 选哪个 offer：OpenClaw 配置服务 / LLM 成本审计 / 其他？
2. 允许发到哪个单一渠道和账号？
3. 对方应该通过什么方式联系你？
4. 目标对象或受众是谁？1-3 个真实对象或一个明确受众；不要提供不必要的个人隐私。
5. 发布后观察多久（24h / 48h）、哪些回复需要我代写但不外发？

Next safe command
- 不发布。
- 不新增交付功能。
- 把授权请求写入本轮记录，等待用户确认或切换到本地可验证任务。
```

获得授权后的最小动作也要保持窄范围：

```text
Single-channel release
- Re-read publish preflight.
- Confirm final copy contains contact path, target audience scope, and observation window boundary.
- Publish once.
- Save published URL, timestamp, channel, and exact copy.
- Observe replies inside the approved window.
- Decide: Continue / Narrow / Stop / Switch.
```

## 反例 / 修正

反例：

> “发布帖已经写好了，价格和交付范围也明确。虽然还没确认渠道，但我可以先替用户发到一个常见社区试试。”

修正：

> “发布素材已准备好，但 `Offer / 实验`、`Channel / account`、`Contact path`、`Target audience / authorized targets` 和 `Observation window` 未全部确认。本轮不外发，不继续扩交付物；只提交授权请求 brief，并切换到本地可验证任务。”

反例：

> “没有渠道授权，那我再补一个更完整的 FAQ、首轮回复自动化和客户 onboarding。”

修正：

> “当前 bottleneck 是授权，不是交付能力。除非 FAQ 能直接减少授权问题，否则停止扩展 offer 资产；下一步只问五个授权字段。”

## 坑

- **把“用户想赚钱”当成“用户允许外发”**：商业目标不等于渠道授权。
- **把历史授权泛化到新渠道**：曾经允许写草稿，不代表允许发布；曾经允许发 A 渠道，不代表允许发 B 渠道。
- **忽略目标对象或受众**：没有明确受众的发布会把内容发给错误人群，或者迫使 Agent 在无人值守时猜测目标——一个模糊受众不等于授权联系真实对象。
- **无人值守跨渠道发布**：多渠道会放大误解、重复回复和撤回成本，尤其不适合 cron。
- **用继续打磨逃避决策**：如果连续多轮都只在补交付物而没有真实渠道反馈，应把状态标成 `Switch` 或 `Wait for authorization`。

## 检查

提交或汇报前检查：

- 是否明确写出 `Decision: Publish / Wait for authorization / Narrow / Switch`？
- 如果是 `Publish`，是否五个字段都有用户明确授权：Offer / 实验、渠道和账号、联系路径、目标对象或受众、观察窗口？
- 是否只选择一个渠道，并记录发布 URL、时间和原文？
- 如果是 `Wait for authorization`，是否停止外发和停止新增交付功能？
- 授权请求是否压缩成用户能直接回答的 5 个问题？
- notebook 或最终报告是否说明哪些 dirty path、offer 资产或渠道没有被接管？
- 落地页 `mailto:` 只是联系入口，不等于渠道授权或需求证据；不能用本地准备好的草稿、样例报告或 package 替代任一字段。
