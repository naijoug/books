# 先确认 Green Baseline，再切换资产任务

**问题**：连续修完 lint、format、test 或 build 后，Agent 为什么不能直接继续扩测试、写总结或切换到教程/书稿？因为如果没有先证明项目已回到可交付状态，下一轮会在“看起来已修好”和“其实仍有红灯”之间漂移；如果已证明全绿却继续打磨同一区域，又会把心跳用成低价值维护。

**要点**：

- 连续修复工程红灯后，先跑项目级聚合入口，例如 `npm run validate`、`pnpm test`、`make ci`、`just check`，确认 lint、format、test、build 或项目约定的等价链路恢复全绿。
- Green baseline 是切换条件，不是额外包装：验证通过后，停止围绕同一批文件机械加覆盖、改格式或补说明，优先转向教程、书稿、技能、收入实验或新的真实边界。
- 如果聚合验证失败，只修最小、明确、可归因的红灯；归属不清的启动前 dirty path 要写入排除边界，不要用 `git add .` 混入。
- 报告里必须同时写清“验证命令和输出摘要”“是否有项目代码改动”“下一段为什么该切换或继续”。
- 若没有聚合入口，先组合现有 lint/test/build 的最小验证链；只有当命令漂移反复阻断交付时，才考虑新增统一 preflight wrapper。

**示例**：

```text
Observation:
上一轮刚修完 util test 的 lint imports，又补了 Prettier 格式；项目已有 npm run validate。

Human hypothesis before agent:
如果 npm run validate 已通过，继续给同一区域补低价值测试的收益低于把经验沉淀成可复用资产。

Verification:
运行 npm run validate，确认 lint、format、全量 tests、production build 全部通过。

Decision:
Switch to asset: 新增 docs/documents/trending/ai/green-baseline-before-asset-switch.md，记录停止规则和报告模板。

Handoff:
下一段可把这条规则提炼成 books/tech-cards-handbook/chapters/ai-agent/ 的正式卡片；不要继续围绕同一批测试文件机械扩展。
```

**反例 / 修正做法**：

```text
反例：
- 只跑目标测试，就说项目已经恢复健康。
- 聚合验证已经全绿，还继续给同一个 hook、context 或 util test 增加低价值断言。
- 项目其实还没验证，却先写方法论文章，把未验证状态包装成经验。

修正：
- 先跑项目级 green baseline。
- 失败则回到最小修复；通过则写明切换理由。
- 切换后交付一个独立资产，并保留原项目的验证输出摘要。
```

**坑**：

- 把 green baseline 当成“本轮无事可做”：验证通过本身也是重要状态证据，但若还有时间，应切换到高复利资产，而不是只写 notebook。
- 把局部测试绿当成项目绿：目标测试只证明改动附近，不能证明发布或交付链路恢复。
- 切换太早：format、lint 或 build 仍失败时，写教程会把失败现场变成未完成债务。
- 切换太晚：全绿后还在同一区域补微小断言，说明交付预算没有生效。

**检查**：最终记录里是否出现了项目级 green baseline 命令、通过/失败语义、切换或继续的决策理由，以及下一段第一条动作？如果只写“测试通过，继续优化”，还没有真正完成 baseline-to-asset 切换。
