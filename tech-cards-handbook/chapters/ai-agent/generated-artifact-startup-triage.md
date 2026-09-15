# 生成产物启动分诊先于工作选择

## 问题

周期性唤醒的 Agent 经常在启动快照里看到 `.qa/`、`coverage/`、`test-results/`、`target/`、临时 sqlite 或 trace 文件。这些路径看起来像“脏工作区”，但来源可能完全不同：上一轮测试留下的噪音、本轮应该交付的 golden output、用户手工保存的诊断材料，或真正需要补 `.gitignore` 的项目问题。若只凭路径名立刻清理、stage 或切换任务，下一轮就失去了判断归属的证据。

启动时的生成产物不是自动可删的垃圾，也不是自动可提交的成果。它先是状态证据；只有完成归属分诊后，才决定继续工程切片、补忽略规则、只写文档资产，还是把问题交给下一轮。

## 要点

- **先拍启动状态，再解释路径。** 在规划前记录相关 repo 的 `git status --short`；生成目录也要进入状态矩阵，而不是被口头忽略。
- **分成三类。** `generated-noise` 是可由路径、ignore 规则或验证日志解释的临时产物；`owned-output` 是本轮命令生成且交付契约要求保留的产物；`unknown-dirty` 是没有归属证据、可能属于用户或其他会话的文件。
- **`git check-ignore` 只是证据，不是删除许可。** 没有 ignore 规则只能说明项目可能缺规则，不能证明目录可以在无人值守时清掉。
- **源码改动与生成目录混在一起时，先保守。** 如果无法证明源码 dirty 与生成产物属于同一任务，默认不接管工程 repo，转向 clean repo 的小任务或写清下一步证据需求。
- **只清理本轮明确创建的产物。** 对启动前已存在的生成目录，除非有明确日志和授权，否则不要 `rm -rf`；最多记录候选 `.gitignore` 建议。
- **notebook 要写出分诊标签。** 交接时不要只写“有临时目录”；要写 `Startup signal / Candidate generated paths / Evidence / Decision / Next safe command`。

## 示例

启动时看到一个测试项目里有 `.qa/` 和 worker sqlite 文件，不要直接删除它们。先把分诊写成可复核记录：

```text
Startup signal:
- study-buddy: clean tracked status; file scan shows .qa/e2e-local-worker-*/tmp/miniflare-*/d1/*.sqlite*

Candidate generated paths:
- study-buddy/.qa/

Evidence:
- Path shape matches local E2E/miniflare output.
- Current run did not create it.
- No current-run command log proves ownership.

Decision:
- generated-noise for planning purposes, but not owned cleanup.

Next safe command:
- git -C study-buddy status --short --ignored=.qa/
- if repeated noise blocks work, inspect .gitignore and propose a path-scoped ignore patch.
```

如果要把它落成最小命令梯，保持只读优先：

```bash
# 1. 启动快照：不修改文件
git -C study-buddy status --short

# 2. 只检查候选路径是否已有 ignore 规则
git -C study-buddy check-ignore -v .qa/ || true

# 3. 若准备补 ignore，先只看目标文件，不清理旧产物
git -C study-buddy diff -- .gitignore
```

只有当本轮命令刚刚创建了某个临时输出，并且命令、时间和路径都能对应时，才可以做 path-specific cleanup：

```bash
# 本轮刚运行的验证命令生成了 .qa/current-run-123/，且该目录不属于交付物
rm -rf .qa/current-run-123/
git status --short
```

## 坑

- **把生成目录等同于授权清理。** `.qa/`、`coverage/` 或 `target/` 很可能是生成物，但无人值守时仍不能删除启动前已有内容。
- **把所有生成物都当噪音。** Golden snapshot、样例包、tracked artifact 和发布目录可能就是交付契约的一部分；它们需要漂移检查，而不是自动恢复。
- **让噪音遮住源码 dirty。** 生成目录旁边若同时有 `M src/...`，必须分别判断归属；不要因为目录像临时文件，就顺手接管源码改动。
- **只在最终报告写“未处理”。** 下一轮需要知道候选路径、判断证据、分诊标签和第一条安全命令。
- **用全仓库清理命令求干净。** `git clean -fd`、`git reset --hard` 会破坏用户或其他 Agent 的未提交工作；短节拍任务应坚持 path-scoped 操作。

## 检查

收尾前确认：

1. 是否在规划前记录了含候选生成路径的启动 `git status --short` 或文件扫描证据？
2. 每个候选生成路径是否已标注为 `generated-noise`、`owned-output` 或 `unknown-dirty`？
3. 若执行了清理，是否只清理本轮命令明确创建的 path，而不是启动前已有目录？
4. 若提交了 generated output，是否有交付契约或漂移检查说明它为什么属于本轮成果？
5. 若选择避开工程 repo，notebook 是否写清了下一轮第一条安全命令，而不是只说“状态不干净”？
6. 最终 commit 的 `git diff --cached --name-status` 是否只包含本轮 owned paths？
