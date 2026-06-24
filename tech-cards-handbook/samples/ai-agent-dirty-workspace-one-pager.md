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

1. 如果上一轮验证或命令输出失败，先判断它是否改变范围、顺序、目标或交接；不要把失败当成背景噪音继续原计划。
2. 如果当前运行在无人值守环境，不能等待澄清；写出默认解释，选择低风险、可验证、可回滚的小动作。
3. 如果接力 path 是 `known-own` 或证据充分的 `previous-agent`，先验证再推进。
4. 如果启动前已有 staged path，单独标记为 `staged/unknown`，不要把 index 状态当作授权。
5. 如果接力 path 是 `user-or-unknown`，记录未接管边界，换 clean repo 的独立小任务。
6. 如果没有合适代码任务，优先沉淀可复用资产：`books/...`、`docs/...`、`skills/skills/...`。
7. 不要把“写 notebook”当成本轮成果；notebook 只记录成果和边界。

## 3. 执行与验证

执行时保持 path-limited，并在 stage 前补一张提交范围台账：

```text
修改前：确认目标 repo 的 git status --short。
修改中：只触碰本轮选择的路径。
台账：列出 repo / path / 启动状态 / 本轮动作 / 是否提交 / 验证证据。
验证：至少做 diff --check；能结构断言就用脚本断言关键词、链接、计数和绝对路径。
提交：只 stage 本轮路径，不使用 git add .；提交前用 git diff --cached --name-status 对照台账。
读回：提交后 rev-parse --short HEAD。
```

最低验证标准：

- 文档类：`git diff --check -- <paths>` 通过；关键词、相对路径、目录索引计数可复核。
- 代码类：运行目标 repo 的测试或最小 smoke test；失败时记录真实错误，不编造通过结果。
- 失败类：验证、测试或命令失败时，必须说明它是否改变本轮范围、顺序、目标或交接；不能只写“失败，下一轮继续”。
- 交接类：notebook 中的 `变更文件` 与实际 staged / committed 文件一致。

一个最小记录示例：

```text
验证：
- git -C books diff --check -- tech-cards-handbook/samples/ai-agent-dirty-workspace-one-pager.md
- python3 - <<'PY'
  from pathlib import Path
  p = Path('tech-cards-handbook/samples/ai-agent-dirty-workspace-one-pager.md')
  text = p.read_text()
  required = [
      'git status --short',
      'path-limited',
      '未接管边界',
      'git diff --cached --name-status',
      'rev-parse --short HEAD',
      'repo / path / 启动状态 / 本轮动作 / 是否提交 / 验证证据',
      '失败当成背景噪音',
      '改变范围、顺序、目标或交接',
  ]
  assert all(x in text for x in required)
  assert '绝对路径前缀' not in text
  PY
提交：
- git -C books add -- tech-cards-handbook/samples/ai-agent-dirty-workspace-one-pager.md
- git -C books commit -m "Improve dirty workspace one pager"
- git -C books rev-parse --short HEAD  # 例如：abc1234
排除：
- makemoney/...：启动前已有 dirty path，未接管、未 stage。
```

## 4. 最终报告模板

收尾口诀：`验证证据 -> 已提交状态读回 -> 排除边界`。先证明本轮改动经过了什么检查，再从 commit 后状态读回 hash / subject，最后点名哪些启动前 dirty path 没有接管。

```text
本轮选择：<为什么选这个小任务>
实际推进：<完成的具体资产或代码改动>
验证证据：<命令 + 结果摘要；未验证项也要写明>
写入 notebook：summaries/hermes/YYYY-MM-DD.md
项目 commit：<repo> <hash> <subject>（如有；从已提交状态读回）
summaries commit：<hash> <subject>（如有；从已提交状态读回）
下一段接力：<下一轮第一步 + verification destination>
未接管边界：<启动前已有或来源不明的 dirty path，说明未 stage>
```

报告里必须同时出现完成项、验证证据和排除项。只报 commit hash、不报未接管边界，会让下一轮误把旧 dirty path 当成本轮成果；只报“验证通过”、不写命令和未验证项，会让读者无法判断这个结论能证明什么。

## 5. 参考卡片

这组参考卡片按 `chapters/ai-agent/README.md` 的 quick path 排列；一页纸只保留操作清单，遇到边界判断时回到对应卡片补细节。

- `books/tech-cards-handbook/chapters/ai-agent/heartbeat-workflow-prevents-drift.md`
- `books/tech-cards-handbook/chapters/ai-agent/startup-snapshot-before-planning.md`
- `books/tech-cards-handbook/chapters/ai-agent/planning-selects-work-not-just-summary.md`
- `books/tech-cards-handbook/chapters/ai-agent/continuation-is-signal-not-obligation.md`
- `books/tech-cards-handbook/chapters/ai-agent/unattended-agent-chooses-default-action.md`
- `books/tech-cards-handbook/chapters/ai-agent/failure-output-must-change-plan.md`
- `books/tech-cards-handbook/chapters/ai-agent/uncommitted-handoff-needs-ownership-triage.md`
- `books/tech-cards-handbook/chapters/ai-agent/staged-changes-are-not-ownership.md`
- `books/tech-cards-handbook/chapters/ai-agent/commit-scope-ledger-prevents-mixed-ownership.md`
- `books/tech-cards-handbook/chapters/ai-agent/dirty-workspace-exit-checklist.md`
- `books/tech-cards-handbook/chapters/ai-agent/verify-before-optimistic-summary.md`
- `books/tech-cards-handbook/chapters/ai-agent/unverified-items-need-explicit-handoff.md`
- `books/tech-cards-handbook/chapters/ai-agent/report-from-committed-state.md`
- `books/tech-cards-handbook/chapters/ai-agent/final-report-names-excluded-boundaries.md`
