# 最终报告要来自已提交状态，不要来自计划中的状态

**问题**：Agent 已经完成修改并准备提交时，为什么最终报告仍可能写错 commit hash、漏掉 notebook 提交，或把“准备提交”的状态说成“已经提交”？

**要点**：

- 最终报告只能引用已提交并读回的状态：先完成目标 repo 提交，再用 `git rev-parse --short HEAD` 和 `git log -1 --pretty=%s` 读回 hash 与标题。
- 如果还要提交工作记录，先把 notebook 写入并提交到记录 repo，再读回记录 repo 的 hash；最终响应同时列出目标 repo 与记录 repo，不能混成一个 hash。
- 没有目标 repo 提交时，也要显式写“无项目提交”并说明原因，例如仅观察规划、目标 repo dirty 无法隔离、或本轮只改 notebook。
- 报告顺序要跟证据顺序一致：验证 → 目标提交读回 → notebook 提交读回 → 最终响应。

**示例**：

```text
错误报告：
- 已提交本轮改动，commit 是 abc1234。

更好的报告：
- books: 7f3a2c1 Add committed-state reporting card
- summaries: 91b8e0d Record Hermes hourly progress for 2026-05-21 18:00
- 项目提交：无（如果本轮没有目标 repo 变更，就这样写明原因）
```

最小操作顺序：

```bash
# 目标 repo，有项目/资产改动时
 git -C books commit -m "Add committed-state reporting card"
 git -C books rev-parse --short HEAD
 git -C books log -1 --pretty=%s

# 记录 repo，notebook 写完后
 git -C summaries commit -m "Record Hermes hourly progress for 2026-05-21 18:00"
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
- 先在 `books` 执行 `git rev-parse --short HEAD` 与 `git log -1 --pretty=%s`，记录项目提交。
- 再在 `summaries` 执行同样两条命令，记录 notebook 提交。
- 最终报告分两行写：`books: <hash> <title>`、`summaries: <hash> <title>`；若某个 repo 没提交，写“无提交”并说明原因。
```

**坑**：

- 从 `git commit` 命令输出、记忆或草稿里复制 hash，没有在提交后读回；一旦提交失败、amend、或切换 repo，报告就会失真。
- 目标 repo 和 notebook repo 都提交了，但最终只写一个 hash，下一轮不知道哪个 hash 对应真正的代码/内容改动。
- notebook 里提前写入“已提交 xxx”，随后实际提交失败或提交标题变化，导致工作记录和 git 历史不一致。
- 在 dirty workspace 里用 `git add .`，把别人的未提交改动混入本轮，再用一个 hash 掩盖边界问题。

**检查**：最终响应里的每个 hash 都能用对应 repo 的 `git rev-parse --short HEAD` 或 `git log -1` 复核；如果某个 repo 没有提交，响应里也要有“无提交/未提交”的明确状态和原因。
