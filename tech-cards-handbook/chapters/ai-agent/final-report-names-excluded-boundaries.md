# 最终报告要写清排除边界，不要只报完成项

**问题**：Agent 在一个 dirty workspace 里完成了本轮小任务，也正确只提交了自己的文件；为什么最终报告仍然可能误导下一轮或用户？

**要点**：

- 最终报告不只列“做了什么”，还要列“哪些已有改动没有接管”。这能保护用户改动、其他 agent 的半成品和本轮未验证的接力点。
- 排除边界必须来自本轮启动和收尾的 `git status --short` 摘要，不要凭记忆写“还有一些改动”。最终报告里要把这类摘要写成独立的“状态证据”，再报告 commit。
- 提交前 index 快照要进入状态证据：`git diff --cached --name-status` 说明“本轮提交实际带走哪些 path”，与启动/收尾工作区状态不是同一件事。
- 项目 repo 与 `summaries` repo 要分开读回：项目成果的 hash、subject、收尾 status 证明资产已落盘；notebook 的 hash、subject、收尾 status 只证明工作记录已落盘。
- 排除边界用相对路径和 repo 名表达，例如 `makemoney` 有未归属的 `docs/interview-qa-day3-publish-kit.md`，不要写绝对路径。
- 如果某个候选任务因为 dirty 状态被放弃，最终报告要把它放到“未接管/下一段接力点”，而不是让读者以为已经处理。
- 排除边界不是免责话术，而是下一轮计划输入：下一轮可以先判断归属，再决定接管、跳过或请求用户确认。

**示例**：

```text
较弱报告：
- 本轮新增 AI Agent 卡片并提交。

更好的报告：
- 本轮选择：在 `books` 新增 AI Agent 卡片。
- 验证证据：`git -C books diff --check -- ...` exit 0；结构断言通过。
- 状态证据：启动时 `docs`、`loom`、`summaries/openclaw/...` 已 dirty/untracked；提交前 index 快照只包含 `books/tech-cards-handbook/chapters/ai-agent/final-report-names-excluded-boundaries.md`；收尾时这些 path 仍未 stage，`books` 项目 repo clean。
- 项目提交：`books` 1a2b3c4 Add final-report boundary card；读回 `books` subject 与收尾 status。
- notebook 提交：`summaries` 5d6e7f8 Record Hermes progress for 2026-06-16 11:00；读回 `summaries` subject 与收尾 status。
- 未接管边界：`makemoney` 仍有启动前已存在的 Day 3 发布包改动；`docs`、`loom` 仍有非本轮改动；`summaries/openclaw/2026-06-12.md` 仍未跟踪。
- 下一段接力：先判断 `makemoney` 的 Day 3 发布包归属；不可确认时继续选择 clean repo 的独立小任务。
```

最小收尾顺序：

```bash
# 1. 提交本轮目标 repo 前后都保留工作区状态证据
 git -C books status --short

# 2. stage 后、commit 前读回 index 快照，只允许出现本轮路径
 git -C books add -- tech-cards-handbook/chapters/ai-agent/final-report-names-excluded-boundaries.md
 git -C books diff --cached --name-status

# 3. 提交本轮目标 repo 后读回项目证据
 git -C books commit -m "Add final-report boundary card"
 git -C books rev-parse --short HEAD
 git -C books log -1 --pretty=%s
 git -C books status --short

# 4. 写 notebook 前再次确认 dirty 边界，避免报告过期
 git -C makemoney status --short
 git -C docs status --short
 git -C loom status --short

# 5. 提交 notebook 后读回记录 repo 证据
 git -C summaries add -- hermes/YYYY-MM-DD.md
 git -C summaries commit -m "Record Hermes progress for YYYY-MM-DD HH:mm"
 git -C summaries rev-parse --short HEAD
 git -C summaries log -1 --pretty=%s
 git -C summaries status --short
```

**可复制最终响应模板**：字段名统一写作 `验证证据`、`状态证据`、`项目提交`、`notebook 提交`，避免在不同卡片之间混用大小写不一致的 notebook 字段或只写 `commit`。

```text
本轮选择：<选了哪个低风险小块，以及为什么没有接管未归属 dirty path>
实际推进：<写清完成的文件、章节、代码或验证脚本；不要只写“已优化”>
变更文件：<本轮实际修改或提交的相对路径；无则写“无”>
验证证据：<列命令和真实结果，例如 diff --check / 测试 / 结构断言>
状态证据：<启动 git status --short、提交前 index 快照、收尾 git status --short 摘要；说明本轮外 dirty path 是否仍未接管>
写入 notebook：summaries/hermes/YYYY-MM-DD.md
项目提交：<repo> <hash> <subject>；读回项目 repo 收尾 status；如没有项目提交，写“无，原因：...”>
notebook 提交：summaries <hash> <subject>；读回 summaries 收尾 status；如未提交，写“未提交，原因：...”>
未接管边界：<repo/path 相对路径 + 启动前已有 / 来源不明 / 验证失败 / 非本轮范围 + 未 stage>
下一段接力：<下一轮第一条可执行动作，而不是泛泛“继续优化”>
```

这个模板适合放在 cron / heartbeat 的最终投递里。它和 notebook 里的记录可以内容相近，但最终响应必须让只看投递摘要的人也知道：本轮成果在哪里、证据是什么、哪些 dirty path 没有被接管。

**反例 / 修正做法**：

```text
反例：
- 其他 repo 有些脏文件，已避开。

问题：
- 没有 repo 名和相对路径，下一轮不知道哪些文件危险。
- 没有说明这些文件是启动前已有、验证失败、还是本轮生成但未提交。
- 用户无法区分“无需关心的构建产物”和“可能需要接力的业务文档”。

修正版：
- 未接管边界：`makemoney/docs/interview-qa-day3-publish-kit.md` 及其计划/指标引用在本轮启动前已存在，未 stage；`docs/documents/trending/ai/README.md` 和 `docs/documents/trending/ai/verification-first-ai-coding.md` 非本轮改动，未 stage；`summaries/openclaw/2026-06-12.md` 非 Hermes notebook，未 stage。
```

**坑**：

- 只写 commit hash，不写未接管边界；下一轮为了“继续推进”可能误把旧脏文件当成本轮成果提交。
- 把 `git status --short` 原样贴成一大段，缺少归属判断；报告变长但没有帮助下一步决策。
- 为了让报告显得顺利而省略失败、跳过和未验证项；这会破坏长期 agent 节拍器的可信度。
- 在 notebook 里写了排除边界，最终响应却省略；用户只看到投递摘要时仍然不知道风险位置。

**检查**：最终报告至少能回答四件事：本轮提交了哪个 repo 的哪些成果；验证命令和启动/收尾状态证据是什么；notebook 记录在哪个文件和哪个提交；哪些启动前已有或未归属的相对路径明确没有接管。若存在 dirty repo，报告里必须有“状态证据”和“未接管边界”或等价表述。
