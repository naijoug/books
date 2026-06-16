# Dirty workspace 收尾要有清单，不要靠最后一眼状态

## 问题

短节拍 Agent 经常在一个已经不干净的 workspace 里工作：有用户改动、其他 agent 的半成品、生成物噪音，也有自己本轮新增的文件。只在结束前跑一次 `git status --short`，容易出现两类错误：

1. 把启动前已有的 dirty path 当成本轮成果提交。
2. 只汇报本轮 commit，忘记说明哪些 dirty path 仍然被刻意排除。

Dirty workspace 不是不能工作，但必须把“启动前状态、本轮范围、提交路径、排除边界、后续接力”做成收尾清单。

## 要点

- **启动状态要留证据**：开始前记录每个相关 repo 的 `git status --short`，尤其是接力点所在 repo。如果某个 path 启动前已经 dirty，默认不是本轮成果。
- **本轮范围要 path-limited**：决定动哪个 repo、哪些文件，就只编辑和 stage 这些路径；避免 `git add .`、跨 repo 扫荡式提交。
- **提交前做四格核对**：
  - 本轮新增/修改：明确可归属、可提交。
  - 启动前已有：除非有证据确认归属，否则不提交。
  - 生成噪音：能安全删除则删除；不能确认则记录不接管。
  - 未验证项：不写成已完成，只写后续接力。
- **最终报告要同时列完成项和排除项**：报告中至少包含 commit hash、变更文件、验证命令，以及仍未接管的 dirty path 类别。
- **notebook 不是成果替代物**：工作记录只说明决策和证据；真正成果应该在书稿、文档、代码、技能或项目文件里落地，并经过验证。

## 示例

一个安全的收尾清单可以写成：

```text
启动前 dirty：
- docs/alpha.md：启动前已修改，未接管
- loom/plans/beta.md：启动前已 staged，未接管

本轮范围：
- books/tech-cards-handbook/chapters/ai-agent/new-card.md
- books/tech-cards-handbook/chapters/ai-agent/README.md

提交前检查：
- git -C books diff --check -- <本轮路径>
- python3 <断言脚本>  # 检查章节结构、索引计数、无绝对路径
- git -C books status --short

提交：
- git -C books add -- <本轮路径>
- git -C books commit -m "Add dirty workspace exit checklist"
- git -C books rev-parse --short HEAD

最终报告边界：
- 未接管 docs/alpha.md、loom/plans/beta.md；下一轮不要视为本轮成果。
```

如果结束时 `git status --short` 仍然显示启动前 dirty path，这不一定是失败；失败是没有说明它们为什么没有被提交、下一轮应该如何处理。

## 坑

- **用“看起来是上一轮写的”替代证据**：除非 notebook、diff、commit 记录或用户说明能证明归属，否则不要接管。
- **提交 summary 时顺手 stage 其他目录**：summary repo 与项目 repo 分开提交；每个 repo 都要独立检查、独立 path-limited stage。
- **把未验证项写成计划内完成**：例如“准备发布”不是“已发布”，“草稿链接待补”不是“分发完成”。
- **最终报告只写好消息**：下一个 agent 需要知道哪些 path 仍然脏、哪些边界不能碰。

## 检查

收尾前问五个问题：

1. 我是否保存了启动前 `git status --short` 的关键信息？
2. 本轮 stage 的每个 path 是否都能解释为本轮创建或本轮明确修改？
3. 是否对本轮文件跑过 `diff --check`、结构断言或项目测试？
4. 最终报告是否包含 commit hash 和相对路径，而不是绝对路径？
5. 是否明确列出了未接管的 dirty path 和下一轮处理规则？

只要其中任意一个问题答不上来，就先暂停提交，回到归属判断和验证步骤。
