# 启动快照先于规划，不要凭上一轮印象选任务

## 问题

心跳型 Agent 很容易一醒来就沿着上一轮的 `Next path` 往下做，尤其是 notebook 写得很清楚时。但 workspace 是活的：用户可能刚改过文件，另一个 agent 可能留下半成品，某个 repo 可能从 clean 变成 dirty。如果不先保存启动快照，后面的规划会把“上一轮建议”误当成“当前可安全执行”。

启动快照不是冗长审计，而是在规划前回答一个问题：本轮看到的状态，哪些是开始前就存在的，哪些才可能归属于本轮？

## 要点

- **先记录时间和节奏**：写清当前时间、这是定时心跳还是用户即时请求。短节拍任务要优先找小而可验证的推进点。
- **先看 workspace root 和相关 repo 状态**：根目录不是 git repo 时也要说明；对候选工作涉及的 sub-repo 跑 `git status --short`，不要只检查最终选中的 repo。
- **把上一轮交接当作输入，不当作命令**：`Next path` 和 `Next slice` 只是候选信号；如果对应 path 启动前 dirty 且归属不明，就要降级为观察项。
- **给 dirty path 打标签**：至少区分 `known-own`、`previous-agent`、`user-or-unknown`、`generated/noise`。没有证据时默认是 `user-or-unknown`，不能 stage。
- **规划必须引用快照证据**：选择理由里要说明为什么避开某些 dirty repo，为什么当前 repo 是低风险、可验证的小任务。

## 示例

一个最小启动快照可以这样写进 notebook 的“上一段/当前状态”：

```text
当前时间：16:00，定时心跳。
workspace root：不是 git repo。
repo 状态：
- books：clean，可作为低风险书稿推进对象。
- makemoney：启动前已有 docs/foo.md、site/bar.html 未提交，归属不明，本轮不接管。
- summaries：仅存在 openclaw/2026-06-12.md 未跟踪，不属于 Hermes notebook，本轮不 stage。
上一轮交接：建议继续 makemoney Day 3 发布包；但相关 path 启动前 dirty，归属证据不足，降级为候选而非执行对象。
```

有了这个快照，规划就能自然推出：本轮不碰 `makemoney` 的未知 dirty path，改选 `books/tech-cards-handbook/chapters/ai-agent/` 中一张独立卡片，并在最终报告列出未接管边界。

## 坑

- **只读 notebook，不跑 git status**：上一轮记录的是过去状态，不代表当前状态。
- **只检查最终选中的项目 repo**：如果候选工作来自多个 repo，却只看最后选中的项目 repo，会漏掉为什么其他候选被排除。
- **把 dirty path 写成“待提交”**：启动前已 dirty 的 path 只能写“未接管”或“需归属判断”，除非有明确证据证明它是本轮或可接管上一轮产物。
- **快照太重导致不行动**：快照只需要支撑本轮决策，不需要遍历整个 workspace 的所有历史和 diff。
- **summary repo 顺手混入其他记录**：Hermes notebook 可以提交；其他 agent 的 summary 文件如果不是本轮任务，就保持未接管。

## 检查

规划前问五个问题：

1. 我是否记录了当前时间和本轮节奏？
2. 我是否检查了 workspace root 以及候选工作相关 repo 的 `git status --short`？
3. 上一轮 `Next path` 是否仍然 clean 或有足够证据可接管？
4. 启动前 dirty path 是否已经标注为 `known-own`、`previous-agent`、`user-or-unknown` 或 `generated/noise`？
5. 本轮选择理由是否能从启动快照推出，而不是只复述“上一轮建议继续”？

如果第 2、3、4 个问题答不上来，就先不要编辑项目文件；补快照，再重新规划。
