# 未提交接力文件先判断归属，不要直接接管

**问题**：上一轮记录的接力点正好对应 repo 里的未提交文件，下一轮 Agent 能不能直接继续改、一起提交？

**要点**：

- 未提交文件不是天然的“可接管工作区”；它可能来自用户、另一个 Agent、失败生成物，也可能是上一轮已验证但未提交的产物。
- 先把文件归属分成四类：`known-own`（本轮明确生成）、`previous-agent`（有 notebook、diff 和验证记录可对应）、`user-or-unknown`（来源不明或可能是用户手改）、`generated/noise`（缓存、构建产物、临时文件）。
- 编辑前结合用户授权确认保留范围；能保留已有修改时继续。只有任务包含提交时才 stage，且需核对具体 diff，路径归属不等于路径内全部改动都可提交。
- `user-or-unknown` 先查 diff 和本次授权；仍不明确或冲突时仅暂停受影响部分，选择原任务内独立小块，并写清边界。
- 判断依据必须来自可观察证据：`git status --short`、path-limited diff、最近 notebook、验证命令输出，而不是“看起来像上一轮做的”。
- 最终报告必须保留状态证据：写清启动快照、收尾 `git status --short`、本轮实际 stage/commit 的 path，以及项目 repo 与 `summaries/` repo 各自的 commit hash；未接管的启动前文件也要列为排除边界。

**示例**：

```text
接力点：继续 Day 3 发布包。
启动状态：`makemoney/docs/interview-qa-day3-publish-kit.md` 已经未跟踪，计划和指标文件也有修改。
归属判断：notebook 只说下一段优先判断这些文件是否可接管，本轮启动前已存在，不能算 known-own。
决策：先只读核对发布包和已有改动，不 stage 未明确授权的 diff；继续本项目独立且已授权的验证工作。
状态证据：最终报告写明发布包未知改动未接管，列出本轮验证结果；没有提交就写未提交，不为填报告字段另建卡片。
```

**反例 / 修正做法**：

```text
反例：
看到 `git status` 里有 `docs/interview-qa-day3-publish-kit.md`，又看到上一轮写了“继续 Day 3”，
于是直接补两段文案、`git add docs/`、提交“完成发布包”。

问题：
这个提交混入了启动前已有改动，无法区分用户手写、上一轮 Agent 产物和本轮修正；
最终报告会把未经归属确认的状态说成本轮成果。

修正：
先用 `git diff -- docs/interview-qa-day3-publish-kit.md docs/interview-qa-7-day-launch-plan.md docs/interview-qa-launch-metrics.md`
检查差异，再查最近 notebook 是否有明确验证和 commit 失败记录。
如果仍不能证明归属，就不要 stage；只在 notebook 中写“未接管，原因是启动前已有未提交改动”，并继续原任务内不受影响的部分；跨项目换任务须已获授权。
```

**坑**：

- 把“上一轮接力”误解成“下一轮有权提交这些路径”。
- 用 `git add .` 或 `git add docs/` 把用户改动、生成物和本轮改动一起混进提交。
- 为了让工作显得连续，事后把启动前已有文件描述成本轮新增。
- 只检查 `git status`，不看 diff、notebook 和验证记录，导致归属判断没有证据。

**检查**：如果最终报告里出现某个未提交文件，能否回答五件事：它在本轮开始时是否已存在？启动快照和收尾 `git status --short` 是否都记录了它的状态？本轮对它做了哪一行可复核修改？提交时是否只 stage 了本轮明确相关路径？项目 repo 与 `summaries/` repo 的 commit hash 是否分别读回？如果答不出来，就不要把它纳入本轮成果。
