# AI Agent Skill Reuse Before New Skill One-Pager

用途：当一次观察看起来“值得沉淀成 skill”时，先用这页纸判断是否应该复用已有技能、继续收窄，还是才进入新技能草稿。它配套 [`../chapters/ai-agent/reuse-existing-skill-before-new-skill.md`](../chapters/ai-agent/reuse-existing-skill-before-new-skill.md)，重点不是写更多技能，而是减少下一轮选择成本。

已填写样例可参考 `docs/documents/trending/ai/ai-coding-audit-one-pager-filled-example.md` 和 `docs/documents/trending/ai/ai-coding-audit-result-log-filled-example.md`：前者用一条脱敏 CI lint 失败观察演示如何保持 `Narrow`、先复用已有技能，并把 `Next evidence needed` 写成下一轮可执行请求；后者把同一类证据不足线索写进 Audit Result，演示为什么“缺原始失败命令和 exit code”只能收窄，不能升级成新 skill 或公开案例。这里故意使用路径文本而不是书内链接，因为样例位于 `docs/` 仓库，不属于本书链接校验范围。

## 30 秒入口判断

| 当前信号 | 先复制哪段 | 暂时不要做什么 |
|---|---|---|
| 只有一条观察，且证据不完整 | `观察快照` + `复用路径` | 不要新建 skill |
| 只有一条 `Narrow` 结果记录 | `观察快照` + `停止条件` | 不要把结果表当成技能化证据 |
| 不知道下一条安全命令 | `复用路径` 的 Step 1 | 不要把测试清单伪装成 skill |
| 不确定哪些内容能公开 | `复用路径` 的 Step 2 | 不要写案例标题或营销 claim |
| 已有两到三条相似观察 | `技能化门槛` | 不要跳过旧技能查重 |
| 新 skill 会让入口更多 | `停止条件` | 不要为了资产感继续拆分 |

## 观察快照

```text
Observation title:
Pain quote:
Evidence shape:
Current decision: Continue / Narrow / Stop
Missing evidence:
Existing skill candidates:
```

填写规则：`Pain quote` 写用户或现场原话；`Evidence shape` 只写已存在材料，例如失败命令、diff、日志、PR 链接、交付物片段；`Missing evidence` 必须能转成下一条动作，不能写“还要更多数据”。

## 复用路径

```text
Step 1 - next-safe-command-ladder
Current biggest risk:
Next safe command:
Pass means:
Fail means:

Step 2 - audit-evidence-boundary
Facts:
Inferences:
Private / do-not-publish:
Allowed claim:

Step 3 - decision
Decision: Continue / Narrow / Stop
Next evidence needed:
Do we need a new skill now? yes / no
Why:
```

默认判断：只要 Step 1 或 Step 2 还能给出清楚输出，就先复用旧技能；只有旧技能无法表达稳定输入、输出和停止条件时，才进入技能化门槛。

## 技能化门槛

新 skill 至少同时满足：

- 已有两到三条相似观察，且不是同一个项目的同一次事故。
- 每次都需要同一组输入字段，而不是临时解释上下文。
- 输出能指导下一条动作，例如命令、边界标签、报告字段或停止条件。
- 验证方式清楚：能用 diff、测试、链接检查、样例断言或人工复核标准证明它生效。
- 新 skill 会合并或替代旧路径，而不是制造第三个相近入口。

## 停止条件

如果出现任一情况，保持 `Narrow` 或 `Stop`，不要新建 skill：

- 只有一个脱敏样例，尚未看到重复性。
- 只有一条 Audit Result，且决策仍是 `Narrow`：它可以证明下一条证据请求是什么，不能证明已经形成稳定技能输入。
- 最大问题只是“还没写清楚”，可以通过文档、书稿卡片或报告模板解决。
- 公开边界不清，无法区分 facts、inferences 和 private 信息。
- 新 skill 的名字必须包含特定项目、特定工具或特定错误码才说得清。
- 写完后下一轮仍需要在多个相似技能之间猜入口。

## 最小交接句

```text
本轮观察保持 Narrow：已用 next-safe-command-ladder 得到下一条安全命令，用 audit-evidence-boundary 标出 facts / inferences / private；当前只有一条样本，不新建 skill。下一段先补 Next evidence needed，再判断是否达到两到三条相似观察的技能化门槛。
```
