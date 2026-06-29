# AI 生成 PR 需要单独审查入口，不要混进普通代码审查

**问题**：团队开始用 agent 写代码后，为什么普通 PR 模板不够用？为什么需要为 AI 生成 PR 单独设计审查入口，而不是只让 reviewer 看 diff？

**要点**：

- AI 生成 PR 的风险不只在代码 diff，还在工作流证据：启动前 workspace 是否干净、agent 是否接管了不属于自己的改动、验证命令是否真实运行、失败输出是否改变了计划。
- PR 模板要先要求作者交代“本次是不是 AI-assisted change”，再记录启动前 `git status --short` 摘要、已接管 path、排除 path 和未验证项。
- reviewer 的第一优先级不是格式或风格，而是范围边界：本轮提交是否只包含声明过的文件，是否混入了用户或上一轮 agent 的未归属改动。
- 每个 AI 生成 PR 都要有验证梯：已跑命令、失败命令、不能跑的原因、下一条安全命令。没有验证梯时，不要把“看起来没问题”当作可合并信号。
- 审查结论用 `Continue / Narrow / Stop` 收束：继续合并、缩小范围重做，或停止自动化并转人工排查。不要只写“LGTM”或“需要修改”。
- 把 PR 模板接到 issue template、mock report 和 handoff 模板上，让一次 review 的证据可以继续变成后续审查样本或收入实验材料。

**示例**：

```text
AI-assisted PR review entry

## Snapshot
- Is this AI-assisted? yes / no
- Starting `git status --short` summary:
- Files intentionally changed:
- Existing dirty paths not owned by this PR:

## Verification ladder
1. Command run:
   Result:
2. Command run:
   Result:
3. Not run / blocked:
   Reason:

## Handoff
- Unverified items:
- Failure output that changed the plan:
- Next safe command:
- Continue / Narrow / Stop recommendation:
```

reviewer 可以按这个顺序看：

1. 先对照 PR 文件列表和“Files intentionally changed”，确认没有混入未声明 path。
2. 再看验证梯是否覆盖本轮改动的最小风险面，而不是只跑了无关格式检查。
3. 再看失败命令是否被吸收到计划里：失败后是否缩小范围、改验证顺序或显式交接。
4. 最后才看代码细节；如果前 3 步缺失，先要求补证据，不要进入普通 code review。

**反例 / 修正做法**：

```text
反例：
- PR 描述：AI 帮忙重构了一下，已测试。
- Reviewer：看 diff 没问题，LGTM。

问题：
- “已测试”没有命令、结果和失败边界。
- 不知道 agent 启动前是否已有 dirty path。
- 不知道本次是否混入了其它任务或用户手写改动。

修正版：
- PR 描述列出启动状态、接管 path、排除 path。
- 验证梯至少包含一条聚焦命令和一条更高层命令。
- 如果验证失败，记录下一条安全命令和 `Narrow` 结论，而不是继续合并。
```

**坑**：

- 把 AI 生成 PR 当成普通 PR，只看 diff，不看 agent 的输入、工具输出和未验证项。
- 模板字段太多，作者随手填“无”；字段宁可少，但必须包含状态、范围、验证、交接和结论。
- 只记录成功命令，不记录失败命令。失败输出才是判断 agent 是否真的修正计划的关键证据。
- reviewer 看到“AI-assisted”就要求重写全部代码；更好的做法是先按范围和证据判断是否 `Continue`、`Narrow` 或 `Stop`。
- 没有把 PR 证据沉淀为样本，导致每次 review 都从零解释同样的 dirty workspace、验证梯和 handoff 问题。

**检查**：PR 模板是否能让 reviewer 在 3 分钟内判断 AI 改动范围；是否记录启动状态、接管 path、排除 path、验证命令和未验证项；是否要求 `Continue / Narrow / Stop` 结论；失败输出是否会改变计划；PR 证据是否能复用到 issue template、AI coding audit 报告或下一轮 agent handoff。