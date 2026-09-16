# Dirty target file blocks continuation

## 问题

上一轮 notebook 已经明确写了“下一次优先检查 A、B 文件”，但本轮启动快照显示这些目标文件在任务开始前已经是 dirty。Agent 还要不要顺着接力点继续改？

## 要点

- **目标文件 dirty 会改变接力语义。** 接力点只说明“优先检查”，不等于授权接管启动前未知 diff；一旦目标文件 dirty，先把它降级成只读 intake。
- **先分三类证据。** `owned-dirty` 需要当前会话生成证据、上一轮提交范围台账或用户授权；没有证据就是 `unknown-dirty`；只出现在其他 agent summary 中则是 `foreign-summary`。
- **只读 intake 不能顺手修。** 可以读 diff、判断风险、写下一步，但不要在同一目标文件上追加“小修”，否则提交时无法证明哪些行属于本轮。
- **用 clean replacement 保持产出。** 如果目标文件无法接管，优先切到 clean repo / clean file 的小资产切片，而不是把本轮成果降为 notebook。
- **回归条件要可执行。** 交接里写清“何时回到原目标”：例如目标 repo 恢复 clean、用户授权接管 dirty path、或上一轮 owner 提供 path-scoped handoff。

## 示例

启动快照显示上一轮目标已经 dirty：

```text
上一轮接力：检查 `docs/.../ai-coding-audit-sample-request.md` 与 `docs/.../ai-coding-audit-roadmap.md` 是否链接 5 项证据字段。
启动快照：两个目标文件均为 `M`，且本轮尚未修改。
ownership：unknown-dirty；没有用户授权，也没有当前轮生成证据。
决策：不在这两个文件上继续编辑；只读记录“目标文件启动前 dirty”。
replacement：切到 clean 的 `books/`，新增一张 AI Agent 卡，说明 dirty target 如何阻断接力。
回归条件：下一轮看到 `docs/` 目标文件 clean，或用户明确授权接管这两个 dirty path，再回到证据字段链接。
```

提交范围台账也要体现这个分叉：

```text
Included paths:
- books/tech-cards-handbook/chapters/ai-agent/dirty-target-file-blocks-continuation.md
- books/tech-cards-handbook/chapters/ai-agent/README.md
- books/tech-cards-handbook/README.md
- books/tech-cards-handbook/chapters/README.md

Excluded startup dirty paths:
- docs/documents/trending/ai/ai-coding-audit-sample-request.md
- docs/documents/trending/ai/ai-coding-audit-roadmap.md
```

## 坑

- 因为目标文件正好是上一轮接力点，就把启动前 dirty 当作继续授权。
- 只读 diff 后顺手改一行，最后无法在 commit 中分清原有改动和本轮改动。
- 发现目标 dirty 后只写 notebook，没有尝试寻找 clean replacement。
- 最终报告只写本轮做了什么，没有写哪些接力目标因为 dirty 被排除。
- 把其他 agent 的 summary 或未跟踪 notebook 当成可代提交材料。

## 检查

- 启动快照里是否标出了目标文件在本轮前已经 dirty？
- 是否能给出接管该 dirty path 的证据？如果不能，是否保持只读并切到 clean replacement？
- 本轮 commit 是否只包含 included paths，而没有混入启动前 dirty path？
- notebook 和最终报告是否同时写明 blocked continuation、replacement work、回归条件和排除边界？
