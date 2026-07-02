# 先跑 30 分钟路线，不要先产品化

## 问题

AI 编程审查的机会看起来很容易产品化：做一个 landing page、打包咨询套餐、写完整 playbook、开发自动审查工具。但在没有真实样本和付费信号前，过早产品化会把时间花在包装、自动化和定位词上，而不是验证一个开发者是否愿意交出真实证据。

更稳的动作是先跑一条 30 分钟路线：发出样本征集，收束首次回复，判断证据是否足够，交付下一条安全命令或 1 页首份报告，再用 `Continue / Narrow / Stop` 决定是否继续。

## 要点

- **先验证证据供给**：真正的信号不是点赞，而是有人愿意提供 PR、agent log、失败命令、reviewer comment 或脱敏 final report。
- **每一步都要有出口**：30 分钟路线不是迷你咨询，而是用 `Continue / Narrow / Stop` 判断下一步。没有授权、没有证据或范围过大时，直接 `Stop` 或 `Narrow`。
- **输出先小后硬**：材料不足时只交付 `Next evidence needed`；材料足够时交付 1 页报告，可直接用 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md)；不要一开始承诺完整工作流改造。
- **公开前先分层 claim**：任何案例、短帖或复盘都先标 `Fact`、`Inference`、`Unverified`、`Private`、`Stop`，不要把样本写成未经授权的战报。
- **产品化来自重复信号**：只有同一类问题重复出现，并且有人愿意补证据、给预算或复用模板，才把它升级成付费审查、模板包、skill 或工具。

## 示例

```text
30 分钟路线：
00:00-05:00 复制样本征集短帖，发到一个真实开发者渠道。
05:00-10:00 收到回复后，只问目标、范围、证据、公开边界和期望输出。
10:00-20:00 判断样本是否足够支持只读审查。
20:00-30:00 输出下一条安全命令梯、Next evidence needed，或 1 页首份报告草稿。
           如果样本足够，复制 books/tech-cards-handbook/samples/ai-agent-audit-report-one-pager.md；
           如果样本不足，只填 Evidence inspected / Unverified items / Next evidence needed。

收口：
- Continue：对方补了具体证据，并愿意进入 PR / 持续审查。
- Narrow：只有一个失败命令或一段 log，先做更小判断。
- Stop：需要生产权限、密钥、未脱敏私有数据，或授权不清。
```

如果收到的是一句“我们团队也遇到过 AI 写代码不稳定”，不要马上写产品介绍。更好的回复是：

```text
我先不判断整体流程。请任选一种证据：
1. 一段失败命令和 exit code；
2. 一个脱敏 PR 摘要；
3. agent final report 里你最不放心的一段；
4. reviewer 留下的一个具体疑问。

我会只读输出：Fact / Inference / Unverified、下一条安全命令、Next evidence needed，以及 Continue / Narrow / Stop。
```

## 坑

- **把路线图当产品页**：还没有样本时就写套餐、价格和自动化能力，会掩盖真正缺口：没人交证据。
- **把 30 分钟变成免费长咨询**：如果对方不断追加大范围背景，但不提供可审查证据，要 `Narrow` 到一个文件、一个命令或一次 PR。
- **用假案例填空**：没有授权样本时只能写模板、骨架和公开边界，不能把匿名案例写成已经发生的战报。
- **只看互动量**：点赞、收藏、转发不是购买信号；补证据、允许脱敏复盘、询问交付方式才是。
- **跳过安全边界**：涉及密钥、生产数据、客户名、绝对路径或未授权私有仓库时，先 `Stop`，再要求脱敏替代证据。

## 检查

准备产品化前检查：是否已经跑过至少一次 30 分钟路线；是否拿到真实可复核证据；是否能把关键判断标成 `Fact`、`Inference`、`Unverified`、`Private` 或 `Stop`；是否交付过 `Next evidence needed` 或基于 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md) 的 1 页报告；是否有 `Continue / Narrow / Stop` 记录；是否出现重复问题和明确购买/复用信号。若答案是否，继续跑样本路线，不要先做产品包装。
