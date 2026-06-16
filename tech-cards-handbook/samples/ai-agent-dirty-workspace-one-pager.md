# Dirty Workspace 心跳接力一页纸

> 用途：当 Agent 被周期性唤醒、workspace 里已经有多个 repo 处于 dirty 状态时，把“先看状态、再选任务、只提交本轮成果、报告排除边界”压缩成可直接复制的执行清单。

## 1. 启动快照

先记录当前事实，不要凭上一轮印象行动：

```text
时间：YYYY-MM-DD HH:mm
workspace root：当前目录是否是 git repo
相关 repo 状态：逐个记录 git status --short
上一轮接力：Next path / Next slice
启动前 dirty path：路径 + 初步归属标签
```

归属标签只用四类：

- `known-own`：本轮已经明确创建或修改，可以继续验证并 stage。
- `previous-agent`：上一轮留下且有 notebook / diff / commit 证据，需要重新验证后才能 stage。
- `user-or-unknown`：来源不明或可能是用户改动，不要改写、不要提交。
- `generated/noise`：缓存、构建产物或临时文件，除非任务要求，否则不要纳入成果。

## 2. 规划取舍

规划必须写出候选项，而不是只复述状态：

```text
上一段/当前状态：上一轮做完什么；当前哪些 repo clean / dirty。
候选工作：至少列出接力项、clean repo 小任务、暂不处理项。
本轮选择：选一个低风险、可验证的小块。
选择理由：说明为什么不接管未归属 dirty path。
下一段计划：留下一个下一轮可直接验证或继续的小动作。
```

选择顺序：

1. 如果接力 path 是 `known-own` 或证据充分的 `previous-agent`，先验证再推进。
2. 如果接力 path 是 `user-or-unknown`，记录未接管边界，换 clean repo 的独立小任务。
3. 如果没有合适代码任务，优先沉淀可复用资产：`books/...`、`docs/...`、`skills/skills/...`。
4. 不要把“写 notebook”当成本轮成果；notebook 只记录成果和边界。

## 3. 执行与验证

执行时保持 path-limited：

```text
修改前：确认目标 repo 的 git status --short。
修改中：只触碰本轮选择的路径。
验证：至少做 diff --check；能结构断言就用脚本断言关键词、链接、计数和绝对路径。
提交：只 stage 本轮路径，不使用 git add .。
读回：提交后 rev-parse --short HEAD。
```

最低验证标准：

- 文档类：`git diff --check -- <paths>` 通过；关键词、相对路径、目录索引计数可复核。
- 代码类：运行目标 repo 的测试或最小 smoke test；失败时记录真实错误，不编造通过结果。
- 交接类：notebook 中的 `变更文件` 与实际 staged / committed 文件一致。

## 4. 最终报告模板

```text
本轮选择：<为什么选这个小任务>
实际推进：<完成的具体资产或代码改动>
写入 notebook：summaries/hermes/YYYY-MM-DD.md
项目 commit：<repo> <hash>（如有）
summaries commit：<hash>（如有）
下一段接力：<下一轮第一步>
未接管边界：<启动前已有或来源不明的 dirty path，说明未 stage>
```

报告里必须同时出现完成项和排除项。只报 commit hash、不报未接管边界，会让下一轮误把旧 dirty path 当成本轮成果。

## 5. 参考卡片

- `books/tech-cards-handbook/chapters/ai-agent/heartbeat-workflow-prevents-drift.md`
- `books/tech-cards-handbook/chapters/ai-agent/startup-snapshot-before-planning.md`
- `books/tech-cards-handbook/chapters/ai-agent/planning-selects-work-not-just-summary.md`
- `books/tech-cards-handbook/chapters/ai-agent/uncommitted-handoff-needs-ownership-triage.md`
- `books/tech-cards-handbook/chapters/ai-agent/dirty-workspace-exit-checklist.md`
- `books/tech-cards-handbook/chapters/ai-agent/final-report-names-excluded-boundaries.md`
