# 最终报告要写清排除边界，不要只报完成项

**问题**：Agent 在一个 dirty workspace 里完成了本轮小任务，也正确只提交了自己的文件；为什么最终报告仍然可能误导下一轮或用户？

**要点**：

- 最终报告不只列“做了什么”，还要列“哪些已有改动没有接管”。这能保护用户改动、其他 agent 的半成品和本轮未验证的接力点。
- 排除边界必须来自本轮启动或收尾的 `git status --short`，不要凭记忆写“还有一些改动”。
- 排除边界用相对路径和 repo 名表达，例如 `makemoney` 有未归属的 `docs/interview-qa-day3-publish-kit.md`，不要写绝对路径。
- 如果某个候选任务因为 dirty 状态被放弃，最终报告要把它放到“未接管/下一段接力点”，而不是让读者以为已经处理。
- 排除边界不是免责话术，而是下一轮计划输入：下一轮可以先判断归属，再决定接管、跳过或请求用户确认。

**示例**：

```text
较弱报告：
- 本轮新增 AI Agent 卡片并提交。

更好的报告：
- 本轮选择：在 `books` 新增 AI Agent 卡片。
- 项目提交：`books` 1a2b3c4 Add final-report boundary card。
- Notebook 提交：`summaries` 5d6e7f8 Record Hermes progress for 2026-06-16 11:00。
- 未接管边界：`makemoney` 仍有启动前已存在的 Day 3 发布包改动；`docs`、`loom` 仍有非本轮改动；`summaries/openclaw/2026-06-12.md` 仍未跟踪。
- 下一段接力：先判断 `makemoney` 的 Day 3 发布包归属；不可确认时继续选择 clean repo 的独立小任务。
```

最小收尾顺序：

```bash
# 1. 提交本轮目标 repo 后读回证据
 git -C books rev-parse --short HEAD
 git -C books log -1 --pretty=%s

# 2. 写 notebook 前再次确认 dirty 边界，避免报告过期
 git -C makemoney status --short
 git -C docs status --short
 git -C loom status --short

# 3. 提交 notebook 后读回记录 repo 证据
 git -C summaries rev-parse --short HEAD
 git -C summaries log -1 --pretty=%s
```

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

**检查**：最终报告至少能回答三件事：本轮提交了哪个 repo 的哪些成果；notebook 记录在哪个文件和哪个提交；哪些启动前已有或未归属的相对路径明确没有接管。若存在 dirty repo，报告里必须有“未接管边界”或等价表述。
