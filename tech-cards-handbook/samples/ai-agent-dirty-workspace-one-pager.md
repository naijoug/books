# Dirty Workspace 心跳接力一页纸

用途：接续一个已有未提交改动的任务。先确认目标和改动范围，再完成可推进的部分。只有原任务允许跨项目选题时才另选仓库；不要求先读完整卡片目录。

## 1. 启动快照

读取相关 repo 的 `git status --short` 和目标路径 diff，结合当前要求与必要的上一轮交接，记录：

```text
当前目标与完成条件：
相关路径及已有 diff：
授权范围、需保留内容：
本轮可独立推进的部分：
```

归属可标为 `known-own`（当前会话产生）、`previous-agent`（交接证据充分）、`user-or-unknown`（仍需核实）、`generated/noise`（生成物）、`foreign-summary`（其他 Agent 的记录）、`staged/unknown`（暂存区来源未明）。标签帮助定位证据，不能替代用户已经给出的授权。

## 2. 规划取舍

1. 目标、归属和授权范围明确，且能保留已有修改时继续；`dirty` 本身不是阻塞条件。
2. 有冲突或归属不明时，按 [目标文件归属判断](../chapters/ai-agent/dirty-target-file-blocks-continuation.md) 对受影响部分做只读 intake，记录 `blocked continuation` 与恢复条件；继续原任务内独立工作。
3. 无人值守时，在既有授权内采用低风险、可验证的默认解释。缺少必要授权的操作暂停，准备工作仍可推进。
4. 只有用户已授权跨项目选题时才选择 clean replacement；否则保留原目标和阻塞说明，不新增无关卡片充当成果。
5. 验证失败时先判断原因，修复本轮引入的问题；其余失败说明对范围和结论的实际影响。

## 3. 执行与验证

- 保留已有改动，围绕本轮目标实施修改。按风险运行相关检查；无新变化或失败时不重复扩大验证。
- 文案改动用审读和 `git diff --check -- <paths>`；索引或链接用已有 verifier；代码改动用相应测试。不要为证明文案正确而编写只断言同一段关键词存在的测试。
- 只有任务包含提交时才 stage/commit。采用 path-limited 范围，结合 `git diff --cached` 核对具体内容，不能把路径内的全部旧 diff 自动纳入。
- 发现启动前 staged/unknown 或 foreign-summary 时保留其状态，不擅自 unstage、清理或代提交；无法隔离时暂停提交，仍可交付本轮修改和验证。
- 需要 notebook 时，仅更新本任务授权的记录路径。读取提交后的 hash 和收尾状态，避免把计划中的提交写成已完成。

## 4. 最终报告模板

普通任务报告成果、验证和实际限制即可。采用需要固定字段的长期心跳协议时，使用以下模板；未发生的项目写“无”或“未提交”，不能为填字段制造操作。

```text
本轮选择：<原目标与实际范围>
实际推进：<完成的工作>
变更文件：<本轮路径>
验证证据：<命令、结果和未验证部分>
状态证据：<相关路径启动/收尾状态及已有 diff 的保留情况>
写入 notebook：<已授权的记录路径；没有则写无>
项目提交：<实际 commit hash/subject；没有则写未提交>
notebook 提交：<实际 commit hash/subject；没有则写未提交>
未接管边界：<冲突或未知改动、原因；没有则写无>
下一段接力：<确有剩余工作时的第一步与恢复条件；已完成则写完成>
```

提交证据用 `git log -1 --oneline` 读回；状态证据来自当前 `git status --short` 与 diff。验证通过后完成当前目标，不因样本目录尚有未用模板而继续扩展工作。

## 5. 参考卡片

只在相应问题出现时阅读：

- 归属不清：[未提交接力文件](../chapters/ai-agent/uncommitted-handoff-needs-ownership-triage.md)。
- 命令失败：[失败吸收](../chapters/ai-agent/failure-output-must-change-plan.md)。
- 提交范围：[路径级提交边界](../chapters/ai-agent/path-scoped-commit-boundary.md)。
- 完整 prompt 或教学案例：[样本包](ai-agent-sample-pack.md) 的对应附录；其中 10 张精选卡片按需阅读。
- 其他任务：[样本索引](README.md)。
