# AI 辅助 PR 审查路径要像产品阶梯，不要只是一组文章

## 问题

很多程序员已经写了关于 agent 工作流、验证优先、PR 审查、服务化 offer 和资产复利的文章，但读者仍然不知道下一步该做什么：先读哪篇、照着跑哪条命令、能交付什么、什么时候该继续投入。

这时问题不在于内容不够多，而在于缺少一条可执行的产品阶梯：从免费阅读入口，到一次可复核的小审查，再到固定范围服务或工具化资产。

## 要点

把 AI 辅助 PR 审查内容组织成四级阶梯：

1. **入口层**：用一页目录或短帖说明读者为什么需要单独审查 AI 生成的 PR。
2. **方法层**：给出固定步骤，例如启动快照、dirty workspace 归属、验证命令梯、未验证项交接。
3. **交付层**：提供 1 页报告、PR 模板、issue template 或 handoff 模板，让读者能复制到真实 repo；如果是收入实验，优先复用 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md) 的固定字段。
4. **转化层**：用 `Continue / Narrow / Stop` 判断是否继续写内容、做服务、做工具，避免靠点赞误判需求；公开复盘前先用 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) 降级证据不足的 claim。

这条路径和固定范围 offer 的关系是：先用 [`ai-coding-audit-is-fixed-scope-offer.md`](ai-coding-audit-is-fixed-scope-offer.md) 定义边界，再用 audit report 一页纸交付，最后才用 case publishing ladder 判断能否发布匿名/公开案例。不要把“内容产品阶梯”写成脱离交付物的营销漏斗。

每一级都要回答一个具体问题：

| 阶梯 | 读者问题 | 可交付物 |
|---|---|---|
| 入口层 | 我为什么要关心 AI PR 审查？ | 目录路径、短帖、问题清单 |
| 方法层 | 我该怎么审？ | 审查步骤、验证命令梯 |
| 交付层 | 我能拿什么交给团队？ | 1 页报告、PR/issue 模板；收入实验先复制 audit report 一页纸 |
| 转化层 | 这件事值得继续投入吗？ | 观察表、样本请求、付费意向记录 |

## 示例

假设已经有这些材料：

```text
agent-workflow.md
verification-first-ai-coding.md
ai-generated-pr-review-entry.md
ai-coding-audit-service.md
ai-coding-audit-mock-report.md
ai-programmer-asset-flywheel.md
```

不要把它们只列成“相关文章”。更好的路径是：

1. 先从 `ai-generated-pr-review-entry.md` 进入，确认 AI 生成 PR 需要独立入口。
2. 再读 `agent-workflow.md` 和 `verification-first-ai-coding.md`，把审查动作收束到启动状态、工具证据和验证命令。
3. 然后使用 `ai-coding-audit-service.md` 与 `ai-coding-audit-mock-report.md`，把方法变成固定范围交付；如果路径已经迁移到本书样本，直接复制 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md) 填 `Scope / Evidence / Top Risks / Next Safe Command Ladder / Handoff Template`。
4. 最后回到 `ai-programmer-asset-flywheel.md`，记录哪些环节值得变成模板、技能、服务或工具；公开复盘前先用 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) 标注 `Fact / Inference / Unverified`，证据不足就只发布方法笔记或问题清单。

一次真实交付后的转化记录可以这样写：

```text
样本来源：脱敏 PR / agent log / 内部 repo
最强痛点：final report 没写未验证项
读者下一步：复制 PR 模板到下一次 agent PR
信号判断：Narrow，下一篇只写“未验证项交接”
```

## 坑

- **只做内容合集**：链接越多，读者越不知道先做什么；必须给出顺序和退出条件。
- **直接跳到卖服务**：没有样本报告、命令梯或模板时，服务承诺会显得空泛；没有证据形状时，案例复盘也只能写成 claim 过重的宣传。
- **把点赞当需求**：AI 话题容易有泛流量，但真正的需求信号是具体失败场景、可审查样本、报告复用意向和复盘授权边界。
- **缺少反向链接**：单篇文章写完后，如果没有接回目录、报告模板和资产飞轮，很快会变成孤岛。

## 检查

发布或整理一组 AI 辅助 PR 审查内容后，用 3 分钟检查四个问题：

1. 新读者能否在 1 个入口页里找到“先读什么”？
2. 读者能否照着材料完成一次 30-90 分钟的小范围审查？
3. 审查结束后是否有可交付物，而不只是心得？交付物是否能直接映射到 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md) 的字段？
4. 是否记录了 `Continue / Narrow / Stop` 信号，决定下一步写作、服务或工具化方向？公开复盘前是否用 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) 检查 claim 标签和证据形状？

如果任一问题答不上来，下一步不要继续扩写新文章；先补入口路径、交付模板或观察表。
