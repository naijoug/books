# Large dirty diff needs intake receipt

## 问题

心跳式 Agent 经常会遇到上一轮留下的大型 dirty diff：一个章节、一个功能或一组索引文件已经被改了几百行，但没有 commit，也没有清楚说明哪些是人工改动、哪些是 Agent 改动、哪些只是格式化。最危险的做法是“顺手修一个小问题，然后把整份文件提交掉”。这样会把未知归属的改写、格式漂移和本轮小修混成一个 commit，下一轮既无法回滚，也无法判断责任边界。

## 要点

- **先写 intake receipt，再决定是否接管。** 大 dirty diff 不是待办项，而是证据对象；先记录 diff 形状、伴随路径、抽样结论和验证边界。
- **用 stat / numstat 量化规模。** `git diff --stat -- <paths>` 告诉你哪些文件受影响，`git diff --numstat -- <paths>` 告诉你插入/删除是否已经超出“小修”范围。
- **抽样分类 diff shape。** 至少看 README、主文件、附录/索引各一段 hunk，标记是内容新增、结构重排、格式化、标点替换、引用修复，还是多种混合。
- **把标点/格式 churn 当成独立风险。** 如果 diff 大量把中文逗号、冒号、引号、分号替换成英文半角，或把整章标点风格统一改写，先把它标成 `format-churn`；这类改动会掩盖真正内容新增，不能只用“章节审校”概括。
- **区分局部修复和整体 ownership。** 如果本轮只能解释 10 行引用格式修复，就不能提交 600 行章节改写；除非明确接管整组 diff，并能说明它们属于同一交付。
- **把决策写成 Continue / Narrow / Stop / Switch。** Continue 表示整体接管；Narrow 表示只读或只做不提交的小修；Stop 表示需要人工确认；Switch 表示改做 clean 小任务。

## 示例

接管回执可以压缩成一张表，放进 notebook 或 handoff：

```text
Large Dirty Diff Intake
- Paths: books/ai-personal-growth/README.md; books/ai-personal-growth/chapters/07-side-hustles-and-income-diversification.md; books/ai-personal-growth/chapters/appendix.md
- Stat: README small; chapter large rewrite; appendix medium content addition
- Numstat: chapter has hundreds of insertions/deletions
- Sampled shape: mixed content edits + format-churn punctuation rewrite + reference-format repair
- Companion paths: README and appendix appear related to the same chapter handoff
- My ownership this turn: only the intake classification is explainable; the chapter rewrite is not owned
- Decision: Narrow / do not commit chapter group in this turn
- Next safe action: either get explicit ownership for the whole group, or switch to a clean file task
```

如果决定 Continue，提交前还要补一张 commit scope ledger：

```text
Commit Scope Ledger
- Included paths: <all paths being owned>
- Excluded dirty paths: <paths explicitly not touched>
- Verification: <path-limited proof commands>
- Rationale: why these paths form one coherent change
```

## 反例 / 修正

反例：

```text
看到引用校验失败 -> 修了 10 个访问日期 -> git add 整个章节 -> commit "fix refs"
```

这个 commit 实际包含几百行旧的标点、段落和内容改写，却只用“fix refs”描述 10 行小修。下一轮无法判断哪些改动已经被审校。

修正：

```text
先记录 stat / numstat / sampled hunks -> 说明本轮只拥有 10 个引用日期修复 -> 跑引用校验 -> 不提交混合大 diff -> 转向 clean 小任务或等待整体接管授权
```

## 坑

- 把“上一轮 notebook 的接力点”当成自动授权，直接接管所有 dirty 文件。
- 只看 `git status --short`，不看 `git diff --stat` 和 `git diff --numstat`，低估 diff 规模。
- 只抽样主文件，不看 README、appendix、catalog 等 companion paths，导致提交半组变更。
- 用一次验证通过掩盖 ownership 不清：测试绿只能证明当前状态可运行，不能证明未知改动属于本轮。
- 在 summaries 或最终报告中写入本机绝对路径，破坏后续接力的可移植性。

## 检查

- 是否记录了 `git diff --stat -- <paths>` 和 `git diff --numstat -- <paths>` 的结论？
- 是否至少抽样了主文件和 companion paths 的 hunks，并给出 diff shape 分类？
- 如果出现大规模标点、空白或格式替换，是否把它单独标成 `format-churn`，而不是和内容新增混写成“审校”？
- 是否明确写出本轮拥有的是局部修复，还是整组 diff？
- 如果没有整体 ownership，是否避免提交这组 dirty 文件？
- notebook / final report 是否写清 Continue / Narrow / Stop / Switch 决策和下一条安全动作？
