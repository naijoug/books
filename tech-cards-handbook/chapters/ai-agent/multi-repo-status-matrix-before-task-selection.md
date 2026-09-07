# Multi-repo status matrix before task selection

## 问题

心跳式 Agent 常在一个 workspace 里同时看到多个子 repo：有的 clean，有的有启动前 dirty path，有的只有 summary notebook 需要追加。如果直接按上一轮接力点行动，容易出现两种相反事故：要么为了避开 unknown dirty 而什么都不做，只写 notebook；要么为了“推进项目”接管了归属不明的仓库，把别人的改动混入提交。

## 要点

- **先按 repo 而不是按愿望分类。** 启动后把每个候选 repo 标成 `clean`、`owned-dirty`、`unknown-dirty` 或 `summary-only`，再决定任务，不要先选项目再解释状态。
- **clean repo 优先承接小切片。** 当主项目 dirty 且归属不明时，优先在 clean 的 `docs/`、`books/`、`makemoney/` 等仓库选择一个可验证小任务；这比空写总结更有产出，也比接管未知 diff 更安全。
- **owned-dirty 需要证据，不靠记忆。** 只有当启动前 notebook、提交范围台账或用户指令能说明该 dirty path 属于本轮可继续交付，才把它标成 `owned-dirty`；否则默认 `unknown-dirty`。
- **summary-only 不是成果 repo。** `summaries/` 负责记录节拍和接力，不能因为它 clean 且可提交，就把“写 notebook”当本轮唯一产出；它应跟随实际工作提交。
- **选择顺序要写进规划。** 推荐顺序是 `owned-dirty with proof -> clean small slice -> read-only intake -> summary-only record`；只有没有安全切片时，才只做观察和下一步计划。

## 示例

启动快照之后，先填一张选择矩阵：

```text
Repo status matrix
- study-buddy: unknown-dirty; reason=many code paths changed before this turn; action=do not modify or commit
- loom: unknown-dirty; reason=scripts and docs already modified; action=exclude unless explicit ownership appears
- skills: unknown-dirty; reason=README and checker changed before this turn; action=do not add new skill here
- books: clean; candidate=add one AI Agent card and update indexes; verification=tech-cards verifier + diff check
- summaries: summary-only; action=append worklog after actual slice is done

Decision: choose books clean small slice.
Excluded boundary: unknown-dirty repos stay untouched; final report names them separately from included paths.
```

如果所有 product repos 都是 `unknown-dirty`，仍然可以推进一个低风险资产切片：

```text
1. classify repos with git status --short
2. pick one clean repo and one bounded file group
3. run the repo's focused proof checker
4. stage only the chosen paths
5. commit project repo first, then append and commit summaries
```

## 坑

- 看到主项目 dirty，就停止行动，只写“等待用户确认”。
- 把 `summaries/` 的提交当作本轮成果，而没有任何项目、文档、书稿或技能推进。
- 因为上一轮 notebook 提到某个 dirty repo，就默认本轮有权提交其中所有 path。
- clean repo 里选择过大的主题，最后又演变成无法验证的重构。
- 最终报告只写 included commit，没有写明哪些 `unknown-dirty` repo 被排除。

## 检查

- 是否在规划前记录了各候选 repo 的 `clean / owned-dirty / unknown-dirty / summary-only` 分类？
- 本轮选择是否来自矩阵，而不是来自惯性接力点？
- 如果跳过 dirty repo，是否仍尝试在 clean repo 推进一个可验证小切片？
- `summaries/` 是否只记录实际工作，而不是充当唯一成果？
- 最终报告是否同时列出 included paths、project commit、summary commit 和 excluded dirty boundaries？
