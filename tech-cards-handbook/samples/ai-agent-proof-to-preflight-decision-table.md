# AI Agent Proof 到 Preflight 决策表

> 目的：当一轮 Agent 已经写了 proof checker、全量 proof 基线、preflight wrapper 或命令梯中的一部分时，用这张表在 2 分钟内判断“下一步该复制哪份输入”，避免把验证工作写成重复清单。

## 术语口径

- **验证入口速记**：样本包顶部的 30 秒导航，先看本轮“当前最大风险”，再决定入口。
- **当前最大风险**：如果下一步不处理，最容易让本轮结论失真的验证缺口，例如 checker 还没写、全量基线未知、命令开始漂移、失败未交接。
- **入口判断**：不是把所有模板都复制一遍，而是在 proof checker、全量 proof 基线、统一 preflight wrapper、命令梯和交接模板之间只选一个最小下一步。

## 先问四个问题

| 问题 | 如果答案是“否” | 如果答案是“是” |
|---|---|---|
| 本轮改动是否有可被脚本检查的基础契约？ | 先不要写 checker；改用人工检查标准或下一条安全命令梯 | 复制 `ai-agent-proof-checker-one-pager.md` |
| checker 是否已经在全量范围跑过红绿基线？ | 不要写进 AGENTS/preflight/CI；先复制 `ai-agent-full-proof-baseline-one-pager.md` | 进入下一问 |
| 稳定命令是否已经超过三条，且下一轮容易漏跑？ | 继续在 notebook 写清具体命令；必要时用命令梯排序 | 复制 `ai-agent-preflight-wrapper-one-pager.md` |
| 本轮是否仍有未覆盖边界或失败阻断？ | 正常提交并用最终报告字段速查表收尾 | 未覆盖但无失败用 `ai-agent-unverified-handoff-one-pager.md`；被失败阻断用 `ai-agent-verification-failure-handoff-template.md` |

## 决策矩阵

| 当前状态 | 下一份输入 | 不要做什么 | 交接句式 |
|---|---|---|---|
| 只有“应该检查链接/索引/格式”的想法，还没有脚本 | `ai-agent-proof-checker-one-pager.md` | 不要直接把想法写进 preflight 或 AGENTS | “本轮先定义 checker 的输入、输出和失败语义；全量基线留到下一段。” |
| checker 已能检查 changed files，但全量失败清单未知 | `ai-agent-full-proof-baseline-one-pager.md` | 不要把 changed-file 绿灯包装成全量可用 | “changed-file proof 已可用；下一段先跑全量红绿基线并分类失败。” |
| 全量基线已绿，但命令散落在 notebook、README 和最终报告里 | `ai-agent-preflight-wrapper-one-pager.md` | 不要靠记忆拼命令，也不要一次引入重型 CI | “全量 proof 已绿；下一段把稳定命令收束为统一 wrapper，并测试默认/快速模式。” |
| wrapper 已存在，但本轮只知道“还要跑更多测试” | `ai-agent-next-safe-command-ladder-one-pager.md` | 不要列一串无优先级的 lint/test/build | “下一段先写当前最大风险，再选择下一条安全命令和 pass/fail 语义。” |
| 验证命令失败，且失败不属于本轮文件 | `ai-agent-verification-failure-handoff-template.md` | 不要为了完成提交而扩范围修未知 dirty path | “验证被启动前/外部边界阻断；本轮只提交已验证文件，失败证据交接。” |
| 验证通过，但仍有渲染、插件、端到端行为未覆盖 | `ai-agent-unverified-handoff-one-pager.md` | 不要在最终报告里写“完全验证” | “本轮已验证 proof 契约；未覆盖重型构建/运行时行为，下一段第一条命令是……” |

## 最小推进顺序

```text
1. changed-file proof：先证明本轮小改的基础契约。
2. full proof baseline：再证明全量范围是红还是绿，并分类失败。
3. preflight wrapper：只有当全量基线稳定、命令开始漂移时才收束。
4. command ladder：当验证项很多但不确定下一条命令时，用风险排序。
5. handoff template：任何失败或未覆盖边界，都必须进入交接句式。
```

## 收尾检查

- 是否写清“当前状态 -> 下一份输入”的选择理由，而不是机械复制全部模板？
- 是否区分 `changed-file proof`、`full proof baseline` 和 `preflight wrapper`，没有把三者混成一个概念？
- 是否保留失败或未覆盖边界的证据位置？
- 是否在 notebook 中写出下一段第一条命令，而不是只写“继续完善验证”？
