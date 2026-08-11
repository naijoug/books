# 格式 churn 先剥离，不要把语义改动埋进全章重排

## 问题

Agent 接手一份已有 dirty diff 时，常会看到“看起来已经改好了”的大文件：章节结构被压缩、表格被重写、提示词被调整，但同时夹杂全角标点改半角、中文引号改英文引号、空行重排、列表编号重写等格式 churn。直接提交这种 diff 会让 reviewer 很难判断真正的语义收益，也会把未来 blame、回滚和审校成本放大。

这张卡解决的问题是：当启动前已有大 dirty diff，但其中只有一小段语义改动值得保留时，如何先剥离格式 churn，再用小 patch 接管语义变化。

## 要点

1. **先做 diff 分诊，不先修正文**：启动快照里发现大 dirty 文件时，先写文件级判断：哪些是语义收益，哪些是格式 churn，哪些需要回避。
2. **恢复基线再重放语义**：如果 churn 覆盖全文件，优先还原到 HEAD 或原中文排版风格，再只重写需要保留的小节、表格或段落。
3. **把“可保留内容”缩成 patch 单元**：语义变化应该能用一句话解释，例如“把 90 天路线压缩成阶段表，并保留外部证据闸门”。解释不清就先不要接管。
4. **验证风格没有被偷换**：除了 `git diff --check`，还要用内容搜索确认标题、标点、引用、代码围栏和关键锚点没有被全局替换污染。
5. **最终报告写清排除边界**：提交语义 patch 后，报告里明确说明哪些启动前 churn 被剥离、哪些文件没有接管、下一轮如果要继续应从哪里开始。

## 示例

启动时看到一个 600+ 行章节 diff，不要直接 `git add`。先把它拆成接收回执：

```text
Dirty diff intake
- File: books/.../chapters/07-side-hustles-and-income-diversification.md
- Size: 658 changed lines
- Keep candidate: 7.10 90-day roadmap table + external evidence gate
- Churn to remove: Chinese punctuation -> ASCII punctuation, quote style changes, prompt numbering noise
- Safe slice: restore chapter style, then rewrite only 7.10
- Excluded: do not stage unrelated style churn
```

接管时的最小动作可以是：

```bash
# 1. 读清当前 diff 和目标小节
# 2. 还原或手工剥离全章格式 churn
# 3. 只重写目标小节

git diff --stat -- books/.../07-side-hustles-and-income-diversification.md
git diff --check -- books/.../07-side-hustles-and-income-diversification.md
python3 scripts/verify_ai_personal_growth_refs.py
```

提交前确认 diff 已从“全章排版重写”收敛为“一个小节的语义 patch”，例如从 658 行变化收敛到十几行新增和一段旧清单删除。

## 坑

- **把大 diff 当授权**：文件已经 dirty 不代表本轮可以接管全部改动；先判断归属和风险。
- **用格式工具掩盖语义**：全局 prettier、标点替换或 markdown formatter 可能让真正的内容变化不可审。
- **只看 whitespace 检查**：`git diff --check` 只能发现尾随空格等问题，不能证明中文风格、标题层级和引用语义没被改坏。
- **保留 churn 只因“看起来更统一”**：如果项目原本使用中文标点和中文引号，本轮不应顺手改成另一套风格。
- **报告只说“优化了章节”**：必须写清保留了哪一段语义变化、剥离了哪些格式变化。

## 检查

接管大 dirty 文档前，逐项确认：

- 是否先记录了启动前 dirty 文件、diff 规模和归属判断？
- 是否能用一句话说明本轮要保留的语义变化？
- 是否已经剥离全局标点、引号、空行、编号、formatter 等无关 churn？
- `git diff --stat` 是否从大范围重排收敛为小范围语义 patch？
- 是否运行了项目的引用 / 链接 / 章节 verifier，而不是只看人工阅读？
- 内容搜索是否确认关键标题、锚点、表格、停止规则和风格标记仍存在？
- commit 是否只 stage 本轮接管文件，最终报告是否写清未接管边界？
