# 日切换需要新快照，不要继承昨天的授权

## 问题

周期性 Agent 跨过零点后，常把昨天最后一段 notebook 当作当前事实：继续写昨天的 `summaries/hermes/YYYY-MM-DD.md`，沿用昨天的 clean / dirty 判断，或因为昨天建议继续某个 repo 就直接接管今天启动前已有的未提交改动。这样会同时破坏时间线和提交边界。

日切换的核心不是“重新开始”，而是把昨天的接力点降级为候选信号，再用今天的系统时间、今天的 notebook 路径和今天的 repo 快照重新选择一块可验证任务。

## 要点

- **先确认今天的记录文件。** 用当前时间决定 `summaries/hermes/YYYY-MM-DD.md`，不要把零点后的工作追加到昨天文件。
- **昨天接力点只算输入。** 昨天的 `Next safe command`、clean 状态和选择理由不能自动变成今天的授权；今天必须重新跑候选 repo 的 `git status --short`。
- **日切换要重建状态矩阵。** 至少把候选 repo 标成 `clean`、`owned-dirty`、`unknown-dirty`、`summary-only`，并在规划里说明为什么继续、停止或切换。
- **实质 repo 与 summaries 分开提交。** 先提交本轮明确拥有的书稿、文档、代码或技能改动，再在 `summaries/` 内只提交当天 notebook。
- **下一段接力写第一条命令。** 日切换后的 handoff 要写清下次先看哪个文件、跑什么检查、遇到什么状态应停止。

## 示例

零点后的第一轮可以这样压缩流程：

```text
Time: 2026-09-08 00:15 CST -> write summaries/hermes/2026-09-08.md
Tail: yesterday's last handoff says continue loom smoke test
Snapshot:
- loom: unknown-dirty; scripts/debug.sh and docs/testing.md changed before this turn
- books: clean; can add one workflow card and update indexes
- summaries: summary-only
Decision: Switch from loom to books small slice.
Reason: yesterday's handoff is a signal, but today's loom dirty paths have no ownership evidence.
Proof: run tech-cards verifier, diff check, and path-limited status before commit.
Next safe command: if loom is still dirty next time, read only git status; do not stage loom paths.
```

如果昨天的目标 repo 今天仍然 clean，则可以继续，但仍要把新快照写进规划：

```text
Decision: Continue docs catalog fix because docs is clean in today's snapshot.
Guard: do not reuse yesterday's proof output; rerun markdown checker after today's edit.
```

## 坑

- 把新一天第一次 notebook 写进昨天的文件，导致接力时间线不可审。
- 只读昨天最后一段，不重新检查今天的 repo 状态。
- 因为昨天某 repo clean，就在今天接管它启动前已经出现的 dirty path。
- 把 summaries 提交和项目提交混在一起，最终无法区分工作记录与实质成果。
- 在日切换时只写“继续推进”，没有说明停止条件和下一条安全命令。

## 检查

收尾前问五个问题：

1. 当前记录是否写入今天的 `summaries/hermes/YYYY-MM-DD.md`？
2. 是否重新检查了本轮候选 repo 的 `git status --short`，而不是沿用昨天状态？
3. 昨天接力点是否被写成候选信号，而不是默认授权？
4. 项目 repo 提交和 `summaries/` notebook 提交是否分开、且各自只包含本轮相关文件？
5. 后续接力是否包含下一次第一条命令、验证方式和遇到 unknown dirty 时的停止条件？

只要第 2 或第 3 项答不上来，就不要修改项目文件；先补今天的快照，再重新选择任务。
