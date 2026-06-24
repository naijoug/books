# 提交范围台账防止混入未知归属

## 问题

心跳型 Agent 经常同时面对多个 repo、启动前 dirty 文件、自己本轮新增文件和必须写入的 notebook。如果只在最后看一眼 `git status`，很容易把“本轮成果”“启动前未知改动”和“其他 agent 的交接文件”混进同一次提交，导致最终报告无法被下一轮复核。

## 要点

- **提交前先列台账**：在动手前或第一处修改后，写下 `repo / path / 启动状态 / 本轮动作 / 是否提交 / 验证证据` 六列；它不需要单独成文，但要能进入 notebook 或最终报告。
- **只提交台账里标为本轮负责的 path**：`known-own` 可以提交；`previous-agent` 需要重新验证后才可提交；`user-or-unknown` 和 `generated/noise` 默认排除。
- **验证证据要和 path 对齐**：不要只写“跑了测试”；要说明这条命令覆盖了哪些 path，哪些 path 只是人工复核或未验证交接。
- **notebook 和项目 repo 分开提交**：书稿、代码、技能和 `summaries/` 是不同 repo 时，分别做 path-limited stage 与 commit；不要为了省事跨 repo 混报一个 hash。
- **最终报告从已提交台账读回**：提交后用 `git status --short` 和 `git log -1 --oneline` 确认，报告 commit hash，同时列出明确排除的启动前 dirty path。

## 示例

```text
启动快照：
- docs：启动前已有 M documents/awesome/ai/agent.md，归属未知，本轮不接管。
- skills：启动前已有 M skills/cron/hourly-progress/references/final-report-evidence-chain.md，归属未知，本轮不接管。
- books：clean，本轮新增 AI Agent 卡片并更新索引。
- summaries：启动前有 ?? openclaw/2026-06-23.md，不属于 Hermes notebook，本轮不接管；本轮只写 summaries/hermes/2026-06-24.md。

提交范围台账：
| repo | path | 启动状态 | 本轮动作 | 是否提交 | 验证证据 |
|---|---|---|---|---|---|
| books | tech-cards-handbook/chapters/ai-agent/commit-scope-ledger-prevents-mixed-ownership.md | absent | 新增卡片 | 是 | 索引统计、链接扫描、人工五段复核 |
| books | tech-cards-handbook/chapters/ai-agent/README.md | clean | 加入阅读顺序 | 是 | 链接扫描 |
| books | tech-cards-handbook/README.md | clean | 更新卡片数与目录描述 | 是 | 索引统计 |
| summaries | hermes/2026-06-24.md | absent/clean | 追加本轮记录 | 是 | read_file 复核、git status 只 stage 该文件 |
| docs | documents/awesome/ai/agent.md | dirty before start | 未接管 | 否 | 最终报告列为排除边界 |
```

提交时按台账执行：

```bash
git -C books add -- \
  tech-cards-handbook/chapters/ai-agent/commit-scope-ledger-prevents-mixed-ownership.md \
  tech-cards-handbook/chapters/ai-agent/README.md \
  tech-cards-handbook/chapters/README.md \
  tech-cards-handbook/README.md
git -C books diff --cached --name-status
git -C books commit -m "Add commit scope ledger agent card"

git -C summaries add -- hermes/2026-06-24.md
git -C summaries diff --cached --name-status
git -C summaries commit -m "Record Hermes 08:34 books scope ledger"
```

## 坑

- **把台账写成事后美化**：如果直到提交后才补台账，已经失去防混入作用；至少要在 stage 前完成提交范围列表。
- **用 `git add .` 抹掉归属边界**：根目录或 repo 内的全量 add 会把启动前 dirty、生成物和本轮文件一起放进 index。
- **只记录 repo，不记录 path**：`docs dirty` 太粗，下一轮仍不知道哪些文件不能碰；台账必须到相对路径。
- **把 summaries 当作附属品**：notebook 是单独 repo 的交接资产，也要有自己的提交范围和 commit hash。
- **验证与提交范围不一致**：如果只验证了新增卡片，却顺手提交了 README、脚本或配置，就要补相应验证或拆出提交。

## 检查

1. 本轮 stage 前是否列出了每个要提交 path 的相对路径？
2. 启动前 dirty 的 path 是否明确标为“未接管”或“重新验证后接管”，而不是默认为待提交？
3. `git diff --cached --name-status` 是否只包含台账中 `是否提交=是` 的 path？
4. 验证命令或人工复核标准是否能对应到每个已提交 path？
5. 最终报告是否分别给出项目 repo 和 `summaries/` repo 的 commit hash，并列出排除边界？

提交范围台账的目标不是增加文档负担，而是在短节拍、多 repo、无人值守场景里，让“我做了什么”和“我没有接管什么”同样可复核。
