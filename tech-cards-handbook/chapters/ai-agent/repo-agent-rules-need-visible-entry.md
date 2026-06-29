# Repo 里的 Agent 规则要有可见入口，不要只藏在聊天记录里

**问题**：团队已经写了 AI-assisted PR checklist、issue template 或审查流程，为什么下一轮 agent 仍然会漏掉？为什么这些规则应该进入 repo 的 README / AGENTS 入口，而不是只留在一次对话、summary 或 PR 评论里？

**要点**：

- Agent 工作规则必须放在新会话最容易读到的位置：`README.md` 负责告诉人和 agent 这个仓库如何协作，`AGENTS.md` 负责把工具命令、边界和交接要求变成运行规则。
- 不要把“启动前 `git status --short`、接管 path、排除 dirty path、验证梯、未验证项、`Continue / Narrow / Stop`”只写在某次 summary 里；summary 是历史证据，不是下一轮的默认入口。
- README 入口要短：说明什么时候使用 AI-assisted PR checklist，并链接 PR template、issue template、服务指南或 mock report；细节放到 AGENTS 或模板里。
- AGENTS 入口要可执行：列出本仓库常用命令、修改边界、验证命令、handoff block 和失败时的降级策略，让 agent 不需要猜“本 repo 的默认动作”。
- 当规则同时面向人和 agent 时，用同一组字段命名。比如 README 写 `Verification ladder`，PR template 和 AGENTS 也使用同名字段，避免交接时字段漂移。
- 每次新增 agent workflow 资产后，都检查是否需要反向补入口；没有入口的模板会变成“存在但没人用”的沉没资产。

**示例**：

```text
README.md

## AI-assisted PR Checklist
- Before opening an AI-assisted PR, capture the starting `git status --short` summary.
- Link to `.github/pull_request_template.md` for the PR evidence block.
- Use `.github/ISSUE_TEMPLATE/ai-coding-audit.yml` for audit/sample requests.
- Reviewer must decide: Continue / Narrow / Stop.
```

```text
AGENTS.md

## AI-assisted Change Workflow
1. Start with ownership: record starting status, owned paths, excluded dirty paths.
2. Change only declared paths; do not absorb pre-existing staged work by accident.
3. Run the smallest relevant verification ladder first, then broader build checks.
4. If blocked, write: verified / unverified / conclusion wording / next safe command / evidence location.
5. Final report from committed state, including commit hash and excluded boundaries.
```

这样 README 给入口，AGENTS 给执行，PR / issue template 收集结构化证据；下一轮 agent 不需要翻历史 summary 才知道该怎么工作。

**反例 / 修正做法**：

```text
反例：
- 在一次 cron summary 里写了“以后 AI PR 要记录验证命令”。
- 新 agent 只读了 repo README，没有看到这条规则。
- 下一次 PR 仍然写“已测试”，没有命令和未验证项。

修正版：
- README 增加一个 5 行 checklist，指向 PR template 和 issue template。
- AGENTS 增加仓库级 AI-assisted workflow。
- PR template 固定要求填写启动状态、接管 path、验证梯和 Continue / Narrow / Stop。
```

**坑**：

- 只在 summary / notebook 里记录规则，却没有把它提升到仓库入口；下一轮 agent 只能靠偶然读到历史记录。
- README 写成长篇教程，导致真正需要的 5 个字段被淹没；README 负责入口，不负责承载所有细节。
- AGENTS 只列构建命令，不写所有权边界和未验证交接；agent 会知道怎么 build，但不知道哪些 dirty path 不能碰。
- 字段命名不统一：README 叫“测试记录”，PR template 叫“验证证据”，AGENTS 叫“检查项”，最后无法自动对齐。
- 新增 issue / PR template 后不回链到 README 或 AGENTS，模板变成孤岛。

**检查**：repo 是否有一个人和 agent 都能看到的入口说明 AI-assisted change；README 是否链接 PR template、issue template 和关键审查文档；AGENTS 是否写清启动状态、接管边界、验证梯、未验证交接和最终报告要求；字段名称是否与模板一致；新增 workflow 资产后是否同步补入口，而不是只写在历史 summary 里。
