# 最终报告要来自已提交状态，不要来自计划中的状态

**问题**：Agent 已经完成修改并准备提交时，为什么最终报告仍可能写错 commit hash、漏掉 notebook 提交，或把“准备提交”的状态说成“已经提交”？

**要点**：

- 最终报告只能引用已提交并读回的状态：先完成目标 repo 提交，再用 `git rev-parse --short HEAD` 和 `git log -1 --pretty=%s` 读回 hash 与标题。
- 已提交状态不等于 workspace 状态：提交前后都要保留 `git status --short` 摘要，最终响应用独立的“状态证据”说明本轮外 dirty path 是否仍未接管。
- 如果还要提交工作记录，先把 notebook 写入并提交到记录 repo，再读回记录 repo 的 hash；最终响应同时列出目标 repo 与记录 repo，不能混成一个 hash。
- 没有目标 repo 提交时，也要显式写“无项目提交”并说明原因，例如仅观察规划、目标 repo dirty 无法隔离、或本轮只改 notebook。
- 报告顺序要跟证据顺序一致：验证 → 状态证据 → 目标提交读回 → notebook 提交读回 → 最终响应。

**示例**：

```text
错误报告：
- 已提交本轮改动，commit 是 abc1234。

更好的报告：
- 验证证据：`git -C books diff --check -- tech-cards-handbook/chapters/ai-agent/report-from-committed-state.md` exit 0。
- 状态证据：启动时 `docs`、`loom` 已 dirty，未接管；收尾时 `books` clean，启动前 dirty path 仍未 stage。
- 项目提交：books 7f3a2c1 Add committed-state reporting card
- notebook 提交：summaries 91b8e0d Record Hermes hourly progress for 2026-05-21 18:00
- 项目提交：无（如果本轮没有目标 repo 变更，就这样写明原因）
```

最小操作顺序：

```bash
# 目标 repo，有项目/资产改动时
 git -C books status --short
 git -C books commit -m "Add committed-state reporting card"
 git -C books status --short
 git -C books rev-parse --short HEAD
 git -C books log -1 --pretty=%s

# 记录 repo，notebook 写完后
 git -C summaries status --short
 git -C summaries commit -m "Record Hermes hourly progress for 2026-05-21 18:00"
 git -C summaries status --short
 git -C summaries rev-parse --short HEAD
 git -C summaries log -1 --pretty=%s
```

**反例 / 修正做法**：

```text
反例：
- 本轮已提交 books 改动和 notebook，commit 是 a1b2c3d。

问题：
- 没有说明 `a1b2c3d` 属于哪个 repo。
- 没有在提交后读回 `books` 与 `summaries` 各自的 HEAD。
- 如果 notebook 提交失败，最终报告仍会把计划中的状态写成已完成状态。

修正版：
- 先在 `books` 执行 `git status --short`，保存收尾状态证据，确认未接管 path 没被 stage。
- 再在 `books` 执行 `git rev-parse --short HEAD` 与 `git log -1 --pretty=%s`，记录项目提交。
- 写入并提交 notebook 后，在 `summaries` 同样执行 `git status --short`、`git rev-parse --short HEAD` 与 `git log -1 --pretty=%s`，记录 notebook 状态证据和提交。
- 最终报告分字段写：`验证证据`、`状态证据`、`项目提交`、`notebook 提交`；若某个 repo 没提交，写“无提交”并说明原因。
```

**坑**：

- 从 `git commit` 命令输出、记忆或草稿里复制 hash，没有在提交后读回；一旦提交失败、amend、或切换 repo，报告就会失真。
- 只读回 commit，不记录提交前后的 `git status --short`；报告虽然有 hash，但下一轮无法判断本轮外 dirty path 是否被排除。
- 目标 repo 和 notebook repo 都提交了，但最终只写一个 hash，下一轮不知道哪个 hash 对应真正的代码/内容改动。
- notebook 里提前写入“已提交 xxx”，随后实际提交失败或提交标题变化，导致工作记录和 git 历史不一致。
- 在 dirty workspace 里用 `git add .`，把别人的未提交改动混入本轮，再用一个 hash 掩盖边界问题。

**检查**：最终响应里的每个 hash 都能用对应 repo 的 `git rev-parse --short HEAD` 或 `git log -1` 复核；响应里有启动/收尾 `git status --short` 摘要作为状态证据；如果某个 repo 没有提交，响应里也要有“无提交/未提交”的明确状态和原因。
