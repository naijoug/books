# AI 编程审查要先做固定范围 offer，不要一上来卖全栈自动化

**问题**：程序员想把 AI coding 经验变成收入时，为什么“我可以帮你们用好 AI 写代码”很难成交，而一个 60-90 分钟的固定范围审查更容易被真实团队接受？

> 可复制路径：先用 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md) 交付 1 页审查报告；如果要把交付沉淀成公开内容，再用 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) 判断证据是否足够发布、只能匿名化，还是必须停止。

**要点**：

- 先卖风险收敛，不要先卖宏大自动化。买家更容易为“这次 agent 改动有哪些返工风险、下一条安全验证命令是什么”付费，而不是为抽象的 AI 转型口号付费。
- 固定输入：一个 repo、一段最近 agent 改动记录、现有验证命令或 CI 线索、当前 PR / final report / handoff 模板。输入不完整时，先 narrow 成免费诊断或内容选题，不要承诺交付。
- 固定输出：1 页风险报告、5 条优先级建议、下一条安全命令梯、一个可复制 handoff 模板。报告骨架直接复用 [`../../samples/ai-agent-audit-report-one-pager.md`](../../samples/ai-agent-audit-report-one-pager.md)，不要每次临场发明字段；输出越短，越能证明审查能力可重复。
- 明确排除：不接生产权限、不承诺修完所有问题、不替代安全审计、不替团队做泛泛工具选型。固定范围是为了保护交付可信度。
- 审查重点放在 agent 工作流，而不只是代码质量：启动 dirty 状态、提交范围、验证梯、失败交接、未验证项和最终报告是否可复核。
- 把每次人工审查当作产品发现：若同一风险在多个团队重复出现，再沉淀成 checklist、CLI、PR bot 或团队 onboarding 模板；若想写成案例，先按 [`../../samples/ai-agent-case-publishing-ladder-one-pager.md`](../../samples/ai-agent-case-publishing-ladder-one-pager.md) 标注 `Fact / Inference / Unverified`，不要把一次审查包装成未经授权的战报。

**示例**：

```text
一句话 offer：
我会只读审查你们的一次 AI 编程工作流，指出最容易造成返工或错误提交的 5 个风险点，并给出下一轮 agent 执行前必须通过的验证清单。

交付范围：
- 输入：一个 repo、最近一次 agent 改动记录、现有验证命令、final report 或 PR 描述。
- 时间：60-90 分钟异步审查 + 30 分钟复盘。
- 输出：1 页 AI Coding Audit Report。
模板：books/tech-cards-handbook/samples/ai-agent-audit-report-one-pager.md
- 不做：不改生产代码、不接密钥、不承诺覆盖整个系统。

报告骨架：
## Scope
- Reviewed:
- Included:
- Excluded:
- Evidence inspected:

## Executive Summary

## Top Risks
| Priority | Risk | Evidence | Recommended fix |
| --- | --- | --- | --- |

## Next Safe Command Ladder
1.
2.
3.

## Handoff Template
- Changed/observed files:
- Commands run:
- Skipped checks:
- Unverified items:
- Next owner action:

## Continue / Narrow / Stop
```

固定范围审查的关键不是“发现越多问题越好”，而是让买家看完后马上知道：下一轮 agent 应该先跑哪条命令、哪些 path 不能碰、哪些报告字段必须补齐。

若买家允许公开复盘，也不要直接把这份报告改写成案例。先用案例发布阶梯检查证据形状：没有客户授权就只写匿名方法样板；只有公开仓库证据时，把结论拆成 `Fact / Inference / Unverified`；证据不足但很想发布时，结论必须降级成“我会如何审查这类工作流”。

**反例 / 修正做法**：

```text
反例：
- 我可以帮你们搭建 AI 编程工作流、写提示词、接入 agent、提升研发效率。

问题：
- 范围太大，买家无法判断交付边界。
- 没有输入要求，容易被拉进客户内部混乱现场。
- 没有可复核输出，无法证明下一次也能交付。

修正版：
- 本次只读审查一次 agent 代码改动，不改代码。
- 只交付 1 页风险报告、5 条建议和下一条安全命令梯。
- 若复盘后团队愿意提供第二个 repo，再讨论 checklist、模板包或自动化工具。
```

**坑**：

- 把审查写成“AI 工具咨询”，导致买家期待你负责模型选型、流程改造、培训和落地，最后固定范围失效。
- 为了显得专业，把报告扩成十几页；读者看完仍不知道下一条命令是什么。
- 忽略所有权边界，只评价代码风格；真正让 agent 交付失控的常常是启动前 dirty path、staged 归属和未验证项交接。
- 没有区分 `Continue / Narrow / Stop`：所有客户都继续推进会消耗交付信用，有些客户材料不足时应该先停止或缩小范围。
- 把交付样本和发布样本混在一起：审查报告服务买家下一步动作，案例发布服务公开可信度；二者之间必须经过证据形状和 claim 标签检查。
- 一开始就写产品，而没有先用人工审查验证真实痛点、愿付费人群和重复风险。

**检查**：这个 offer 是否能在不接生产权限的情况下交付；输入是否少到买家 10 分钟内能准备；输出是否压缩到 1 页；报告是否包含证据、风险、下一条命令、handoff 和 `Continue / Narrow / Stop`；是否明确链接审查报告一页纸作为交付模板；若要公开发布，是否先经过案例发布阶梯的证据形状、授权边界和 claim 标签检查；复盘后是否能判断下一步是继续服务、缩小范围，还是停止这个收入实验。
