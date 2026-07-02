# AI Coding Audit Report 一页纸

适用场景：你想把 AI 编程经验变成一个 60-90 分钟、只读、固定范围的审查 offer，但还没有可复制的交付物。先用这份一页纸交付首个样本报告，再决定是否继续做咨询、模板包或自动化工具。

## 使用前提

- 只读输入：一个 repo、最近一次 agent/AI coding 改动记录、现有验证命令或 CI 线索、PR 描述 / final report / handoff 任一项。
- 不接生产权限、不接密钥、不承诺修完问题；本交付只回答“下一轮 agent 先做什么更安全”。
- 材料不足时先输出 `Narrow` 或 `Stop`，不要为了成交编造证据。

## 复制模板

```markdown
# AI Coding Audit Report

## Scope
- Reviewed: <repo / PR / handoff / commit range / report path>
- Included: <本轮实际查看的文件、命令、记录>
- Excluded: <未接触的生产环境、凭据、外部服务、全量代码区域>
- Evidence inspected: <真实命令输出、CI 记录、diff、文档或日志位置>

## Executive Summary
- Decision: Continue / Narrow / Stop
- Main reason: <用一两句话说明最主要风险或推进依据>
- Next owner action: <下一轮第一条可执行命令、文件读取或人工检查>

## Top Risks
| Priority | Risk | Evidence | Recommended fix |
| --- | --- | --- | --- |
| P0/P1/P2 | <风险描述> | <具体 path、命令输出或报告字段> | <一条可执行修复或缩小范围动作> |

## Next Safe Command Ladder
1. <最便宜、最贴近当前风险的命令或检查；pass/fail 各代表什么>
2. <通过后再跑的更宽验证；失败时停止并交接什么>
3. <只有前两步通过才需要的构建、smoke 或人工验收>

## Handoff Template
- Changed/observed files: <只列审查实际看到的相对路径>
- Commands run or inspected: <真实命令或 CI job；没有就写无>
- Skipped checks: <没有覆盖的检查和原因>
- Unverified items: <不能得出的结论>
- Next owner action: <下一轮第一条动作>

## Continue / Narrow / Stop
- Continue if: <证据足够、风险可控、下一条验证明确>
- Narrow if: <材料不足、dirty 归属不清、验证入口不稳定>
- Stop if: <需要生产权限、凭据缺失、范围已经越过固定 offer>
```

## 30 分钟填表流程

| 时间 | 动作 | 输出 |
| --- | --- | --- |
| 0-5 分钟 | 读 final report / PR 描述 / handoff，标出声称已完成的结论 | 结论清单 |
| 5-12 分钟 | 对照 `git status`、diff、CI 或命令记录找证据 | Evidence inspected |
| 12-20 分钟 | 选 3-5 个最高返工风险，不补代码，只写现象和后果 | Top Risks |
| 20-25 分钟 | 写下一条安全命令梯，每级都写 pass/fail 语义 | Next Safe Command Ladder |
| 25-30 分钟 | 做 Continue / Narrow / Stop 判断，并写下一轮第一条动作 | Executive Summary |

## 示例风险写法

| Priority | Risk | Evidence | Recommended fix |
| --- | --- | --- | --- |
| P0 | 报告称“已验证”，但只看到格式检查，没有覆盖交互路径 | `final report` 只列 `git diff --check`；未见 smoke 或人工路径 | 下一轮先跑最小交互 smoke；失败则把结论改成“仅格式已验证” |
| P1 | dirty workspace 归属不清，存在混入非本轮改动的风险 | `git status --short` 有启动前修改，但 report 未列排除边界 | 补提交范围台账，只 stage 本轮路径；最终报告列未接管 path |
| P1 | 验证失败没有改变计划，继续新增功能 | 测试失败后仍追加新文件；handoff 无失败归属 | 先用失败交接模板写明失败归属和下一条复现命令 |

## 质量检查

- 报告是否能压缩到一页，读者 3 分钟内知道下一条动作？
- 每个风险是否都有相对路径、命令、CI、diff 或报告字段作为证据？
- 是否明确写了 `Excluded` 和 `Unverified items`，没有把未覆盖项包装成结论？
- 是否真的做了 `Continue / Narrow / Stop` 判断，而不是默认继续服务？
- 是否能在不接生产权限和不改代码的情况下交付？

相关背景：固定范围 offer 见 [`../chapters/ai-agent/ai-coding-audit-is-fixed-scope-offer.md`](../chapters/ai-agent/ai-coding-audit-is-fixed-scope-offer.md)，首份报告策略见 [`../chapters/ai-agent/first-report-before-consulting.md`](../chapters/ai-agent/first-report-before-consulting.md)，命令梯写法见 [`ai-agent-next-safe-command-ladder-one-pager.md`](ai-agent-next-safe-command-ladder-one-pager.md)。
