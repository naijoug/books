# Staged 改动不等于本轮所有权

## 问题

在多 repo、多人或多 agent 接力的 workspace 里，`git status --short` 里的 `A  file`、`M  file` 很容易被误读成“已经准备好由我提交”。但 staged 只说明 index 里有内容，不说明内容是谁放进去的、是否经过当前轮验证、是否属于当前目标。

如果短节拍 Agent 看到 staged path 就顺手提交，风险比普通 unstaged dirty 更高：提交记录会把归属问题固化成历史，下一轮更难判断哪些成果真的被本轮验证过。

## 要点

- **staged 是状态，不是授权**：除非本轮创建、修改并验证了这些 path，或用户明确要求接管，否则不要把启动前 staged 文件纳入本轮提交。
- **启动快照要保留 index 形态**：记录 `A  path`、`M  path`、`MM path` 等短状态；它们决定下一轮是否需要先 `diff --cached` 做归属判断。
- **提交范围必须重新声明**：即使 index 里已经有文件，也要用 path-limited `git add -- <本轮文件>` 和 `git commit -- <本轮文件>` 的思路核对，不要因为 staged 方便就 `git commit` 全部带走。
- **验证只覆盖本轮边界**：如果没有验证启动前 staged 文件，就在最终报告里写成未接管边界，而不是把它藏在“workspace 还有其他改动”里。
- **必要时先读 cached diff，不要先改 index**：`git diff --cached -- <path>` 能帮助判断内容，但不要在未确认归属前 reset、amend 或整理别人的 staged 状态。

## 示例

启动快照：

```text
--- loom
M  docs/PLANS.md
A  docs/plans/2026-06-12/10:46-workflow-stage-navigation.md
```

更安全的本轮决策：

```text
本轮不接管 `loom`：存在启动前 staged 新文件和修改文件，归属未知。
若要继续推进，先打开 notebook 或计划文档寻找证据；没有证据时，只能在另一个 clean path 完成小任务，并在最终报告里列出未接管边界。
```

如果必须在同一个 repo 另开小任务：

```bash
# 只验证、stage、提交本轮文件；不要用 git add .
git -C books diff --check -- tech-cards-handbook/chapters/ai-agent/staged-changes-are-not-ownership.md tech-cards-handbook/chapters/ai-agent/README.md
git -C books add -- tech-cards-handbook/chapters/ai-agent/staged-changes-are-not-ownership.md tech-cards-handbook/chapters/ai-agent/README.md
git -C books commit -m "Add staged ownership card"
```

## 坑

- **把 staged 当作“上一轮已经决定提交”**：上一轮可能被中断、验证失败，或只是临时 stage；没有证据就不要代签名。
- **为了清爽状态重置 index**：`git reset` 可能破坏用户或其他 agent 的工作现场；除非本轮明确负责整理，否则只记录边界。
- **最终报告只说“未接管 dirty path”**：staged path 要单独点名，因为它们更容易在下一次无意中被提交。
- **提交后才发现混入 staged 文件**：提交前用 `git diff --cached --name-status` 复核 index；提交后再补救会增加历史噪音。

## 检查

收尾前确认：

1. 启动前 staged path 是否被记录为相对路径？
2. 本轮提交的每个 path 是否都是本轮明确创建或修改的？
3. `git diff --cached --name-status` 是否只包含本轮要提交的 path？
4. 最终报告是否把启动前 staged path 列入未接管边界？
5. 下一段接力是否说明第一步是归属判断，而不是直接提交？

只要 staged path 的归属无法回答，就把它视为“需要 triage 的交接信号”，而不是“可以顺手提交的半成品”。
