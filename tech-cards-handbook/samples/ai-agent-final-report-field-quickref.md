# AI Agent 最终报告字段速查

> 用途：当 Agent 已经完成验证、准备提交和回复时，用这一页把“验证证据、状态证据、提交读回、排除边界”压缩成固定字段，避免只报完成项、不报未验证项或未接管边界。

## 1. 收尾顺序

不要从“我做了什么”直接跳到最终回复。先按下面顺序收尾：

```text
验证证据 -> 状态证据 -> 已提交状态读回 -> 排除边界 -> 下一段接力
```

- **验证证据**：写真实命令和结果摘要；失败或未覆盖时，引用未验证项而不是改写成“通过”。
- **状态证据**：写启动和收尾 `git status --short` 摘要；如果有启动前 dirty path，说明是否仍未接管。
- **已提交状态读回**：提交后用 `git -C <repo> log -1 --oneline` 读回 hash 和 subject，不从计划或记忆里抄。
- **排除边界**：列出本轮没有接管、没有 stage、没有验证的相对路径；为空也写 `无`，并说明依据。
- **下一段接力**：给下一轮第一条动作和验证目的地，不只写“继续完善”。

在写这些字段前，先把素材分成三层：

- **事实**：已经运行的命令、真实输出、实际变更文件、已读回的 commit hash。
- **推断**：基于事实得到的判断，例如“这个 dirty path 是启动前已有，所以本轮未接管”。推断必须指出依据。
- **计划**：下一轮要做的第一步。计划不能冒充已经完成的事实，也不能写成已验证结论。

最终报告只把事实写成完成项；推断要带证据来源；计划只放在“下一段接力”。这样 notebook 和最终回复才会成为下一轮可复用的工作资产，而不是把执行、解释和愿望混成流水账。

## 2. 固定字段

最终报告字段固定保留；某项没有发生时写 `无` 或 `未提交`，不要删除字段。

```text
本轮选择：<选择的 repo / 文件 / 小任务；为什么优先做它>
实际推进：<完成的具体资产或代码改动>
变更文件：<本轮实际修改或提交的相对路径；无则写“无”>
验证证据：<命令 + 结果摘要；失败或未覆盖项也要写明>
状态证据：<启动 / 收尾 git status --short 摘要；本轮外 dirty path 是否仍未接管>
写入 notebook：summaries/hermes/YYYY-MM-DD.md
项目提交：<repo> <hash> <subject>（如有；从已提交状态读回）
notebook 提交：summaries <hash> <subject>（如有；从已提交状态读回）
未接管边界：<启动前已有或来源不明的 dirty path；为空写“无”>
下一段接力：<下一轮第一步 + 验证目的地>
```

字段顺序本身就是风险控制：先让读者看到证据，再看到提交，最后看到排除项和接力点。

## 3. 提交读回短例

```text
项目提交：books 1a2b3c4 Add final report field quickref
  证据：提交后运行 `git -C books log -1 --oneline` 读回。
notebook 提交：summaries 5d6e7f8 Record Hermes heartbeat progress
  证据：提交后运行 `git -C summaries log -1 --oneline` 读回。
未提交：项目 repo 本轮无可提交改动；仍保留字段，不把计划中的提交写成已落地。
```

如果验证失败导致没有项目提交，也按同一字段写：

```text
项目提交：未提交（验证失败，未 stage；失败证据见“验证证据”）。
notebook 提交：summaries <hash> <subject>。
未接管边界：<失败涉及的启动前 dirty path 或未验证 path>。
```

## 4. 未验证项写法

验证失败、依赖缺失、人工 UI 未覆盖时，不要把结论写成“已完成并验证”。先判断它只是“覆盖不足”，还是已经阻断了目标验证：

- **覆盖不足但验证未失败**：用四段写清已验证范围、未覆盖范围、结论边界和下一步。
- **验证命令已经失败**：先转到 `books/tech-cards-handbook/samples/ai-agent-verification-failure-handoff-template.md`，按失败归属选择下一步第一条动作，再回到最终报告字段里写“未验证”和“下一段接力”。

四段写法固定如下：

```text
已验证：<本轮真实验证过的范围和命令>
未验证：<未覆盖或失败的范围；失败时写失败归属>
结论措辞：<因此只能说什么，不能说什么>
下一步：<下一轮第一条命令、文件读取或人工检查动作；失败时来自失败交接模板的动作选择器>
```

例子：

```text
已验证：`git -C books diff --check -- tech-cards-handbook/samples/ai-agent-final-report-field-quickref.md` 通过；关键词断言通过。
未验证：未运行全书链接检查，因为本轮只新增一页样本并更新两个入口链接。
结论措辞：可以说“本轮文档结构和入口链接已做聚焦验证”，不能说“全书链接全部通过”。
下一步：若继续收尾证据线，运行全书链接检查或只检查新增样本入口。
```

## 5. 日志资产化检查

最终报告不是对 notebook 的复读，而是把 notebook 里的可接力资产压缩出来。发送前做一次快速检查：

```text
事实够不够：有没有命令、输出摘要、文件路径、commit 读回？
推断清不清：有没有把“为什么没接管/为什么只验证到这里”写出依据？
计划可执行吗：下一段能不能按第一条动作直接开工？
边界可复核吗：所有路径是否为相对路径，且没有把旧 dirty path 混成本轮成果？
```

如果某一项答不上来，先补证据或降级措辞；不要用“应该没问题”“已经处理好”填空。

## 6. 排除边界正反例

```text
✅ 未接管边界：loom/docs/PLANS.md 启动前已 staged/modified，归属未知，未修改、未 stage。
✅ 未接管边界：skills/skills/cron/hourly-progress/references/final-report-evidence-chain.md 启动前已 modified，归属未知，未接管。
✅ 未接管边界：无（启动和收尾 status 均无本轮外 dirty path）。
❌ 未接管边界：（字段省略）
❌ 未接管边界：有一些别的改动，没管。
```

边界必须使用相对路径，且要说明证据来自启动或收尾状态；否则下一轮无法判断它是旧改动、用户改动、生成噪音还是本轮漏提交。

## 7. 相关入口

- `books/tech-cards-handbook/chapters/ai-agent/report-from-committed-state.md`
- `books/tech-cards-handbook/chapters/ai-agent/final-report-names-excluded-boundaries.md`
- `books/tech-cards-handbook/chapters/ai-agent/unverified-items-need-explicit-handoff.md`
- `books/tech-cards-handbook/chapters/ai-agent/work-log-is-reusable-asset.md`
- `books/tech-cards-handbook/samples/ai-agent-verification-failure-handoff-template.md`
- `books/tech-cards-handbook/samples/ai-agent-dirty-workspace-one-pager.md`
- `books/tech-cards-handbook/samples/ai-agent-sample-pack.md`
