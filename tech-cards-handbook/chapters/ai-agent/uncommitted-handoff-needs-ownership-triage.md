# 未提交接力文件先判断归属，不要直接接管

**问题**：上一轮记录的接力点正好对应 repo 里的未提交文件，下一轮 Agent 能不能直接继续改、一起提交？

**要点**：

- 未提交文件不是天然的“可接管工作区”；它可能来自用户、另一个 Agent、失败生成物，也可能是上一轮已验证但未提交的产物。
- 先把文件归属分成四类：`known-own`（本轮明确生成）、`previous-agent`（有 notebook、diff 和验证记录可对应）、`user-or-unknown`（来源不明或可能是用户手改）、`generated/noise`（缓存、构建产物、临时文件）。
- 只有 `known-own` 可以直接 stage；`previous-agent` 也要先重新验证、必要时只补最小修正，再用 path-limited staging 提交。
- `user-or-unknown` 不要为了完成接力而改写或提交；如果确实要推进，选择不触碰这些文件的独立小块，并在记录里写清边界。
- 判断依据必须来自可观察证据：`git status --short`、path-limited diff、最近 notebook、验证命令输出，而不是“看起来像上一轮做的”。

**示例**：

```text
接力点：继续 Day 3 发布包。
启动状态：`makemoney/docs/interview-qa-day3-publish-kit.md` 已经未跟踪，计划和指标文件也有修改。
归属判断：notebook 只说下一段优先判断这些文件是否可接管，本轮启动前已存在，不能算 known-own。
决策：不 stage 这些文件；改在 clean 的 `books/` 中补一张 Agent 运行卡片，并记录 makemoney 的边界条件。
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
如果仍不能证明归属，就不要 stage；只在 notebook 中写“未接管，原因是启动前已有未提交改动”，并换一个 clean 小任务。
```

**坑**：

- 把“上一轮接力”误解成“下一轮有权提交这些路径”。
- 用 `git add .` 或 `git add docs/` 把用户改动、生成物和本轮改动一起混进提交。
- 为了让工作显得连续，事后把启动前已有文件描述成本轮新增。
- 只检查 `git status`，不看 diff、notebook 和验证记录，导致归属判断没有证据。

**检查**：如果最终报告里出现某个未提交文件，能否回答三件事：它在本轮开始时是否已存在？本轮对它做了哪一行可复核修改？提交时是否只 stage 了本轮明确相关路径？如果答不出来，就不要把它纳入本轮成果。
