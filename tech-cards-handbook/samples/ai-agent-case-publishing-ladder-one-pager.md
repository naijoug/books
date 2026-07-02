# AI Agent Case Publishing Ladder One-Pager

用途：把一次 AI 编程审查、30 分钟路线或发布反馈，从“首份报告”安全推进到“可公开案例”。它不是战报模板，而是一个降级阶梯：证据足够才公开，证据局部不足就缩成方法样板，授权或证据链断裂就停止。

关联卡片：

- [`../chapters/ai-agent/first-report-before-consulting.md`](../chapters/ai-agent/first-report-before-consulting.md)
- [`../chapters/ai-agent/thirty-minute-route-before-productizing.md`](../chapters/ai-agent/thirty-minute-route-before-productizing.md)
- [`../chapters/ai-agent/publish-feedback-needs-evidence-shape.md`](../chapters/ai-agent/publish-feedback-needs-evidence-shape.md)
- [`../chapters/ai-agent/anonymous-case-must-not-invent-evidence.md`](../chapters/ai-agent/anonymous-case-must-not-invent-evidence.md)
- [`../chapters/ai-agent/public-case-separates-facts-inferences-unverified.md`](../chapters/ai-agent/public-case-separates-facts-inferences-unverified.md)
- [`ai-agent-audit-report-one-pager.md`](ai-agent-audit-report-one-pager.md)

## 30 秒决策

| 当前材料 | 默认动作 | 不要做 |
|---|---|---|
| 只有点赞、收藏、泛泛认可 | `Stop`：只记录 hook 信号 | 不要写成需求验证或客户案例 |
| 有原话或一个失败命令，但没有 PR / log / final report | `Narrow`：补 `Next evidence needed`，只写方法样板 | 不要补全客户画像、收益数字或根因 |
| 有 PR / log / final report，但公开边界未确认 | `Narrow`：先问公开边界和脱敏要求 | 不要默认“匿名后即可公开” |
| 有证据链、授权边界和未验证项 | `Continue`：写匿名案例或公开案例草稿 | 不要删除 `Unverified` 来制造战报感 |
| 涉及密钥、生产权限、合规或未授权私有代码 | `Stop`：停止发布，保留内部学习摘要 | 不要用改名、截图裁剪或 AI 改写绕过边界 |

## 输入证据表

```text
Case Publishing Ladder

1. Source
- 来源类型：30 分钟路线 / 固定范围审查 / 发布反馈 / 公开项目复盘
- 是否真实材料：真实脱敏 / 合成样例 / 公开项目
- 是否允许公开：Yes / No / Unknown

2. Evidence shape
- PR / diff：
- 失败命令或验证命令：
- agent log / final report：
- review comment / 用户原话：
- 缺失证据：

3. Claim labels
- Fact：
- Inference：
- Unverified：
- Private：
- Stop：

4. Publishing decision
- Continue / Narrow / Stop：
- Next evidence needed：
- 可发布形态：匿名案例 / 公开案例 / 方法样板 / 不发布
```

## 从报告到案例的四步

1. **先复制审查报告骨架**：从 [`ai-agent-audit-report-one-pager.md`](ai-agent-audit-report-one-pager.md) 拿 `Scope`、`Top Risks`、`Next Safe Command Ladder`、`Handoff Template` 和 `Continue / Narrow / Stop`，不要从营销标题开始写。
2. **再记录反馈证据形状**：按 [`../chapters/ai-agent/publish-feedback-needs-evidence-shape.md`](../chapters/ai-agent/publish-feedback-needs-evidence-shape.md) 区分 PR、失败命令、agent log、final report、review comment 和泛泛认可。
3. **然后选择公开形态**：真实材料但授权有限时，用 [`../chapters/ai-agent/anonymous-case-must-not-invent-evidence.md`](../chapters/ai-agent/anonymous-case-must-not-invent-evidence.md) 的证据边界；公开项目或可公开材料，用 [`../chapters/ai-agent/public-case-separates-facts-inferences-unverified.md`](../chapters/ai-agent/public-case-separates-facts-inferences-unverified.md) 的 claim 标签。
4. **最后保留未验证项**：案例结尾必须写 `Unverified` 和 `Next evidence needed`。如果这些字段会削弱故事性，说明当前材料还不适合写战报。

## 可复制收口句式

```text
本案例来自一次固定范围 AI 编程审查；路径、业务名和私有上下文已脱敏。
Fact：本轮只验证了 <命令 / 文件 / review comment>，结果是 <摘要>。
Inference：基于这些证据，我们优先判断风险集中在 <范围>，而不是 <未证明范围>。
Unverified：未检查 <生产数据 / 权限 / 浏览器 smoke / 长期指标>。
Next evidence needed：下一步只需要补 <一条命令 / 一个日志片段 / 一个授权确认>。
Publishing decision：Continue / Narrow / Stop，因为 <证据形状 + 公开边界>。
```

## 质量检查

发布或交给下一轮前检查：

- 是否写明来源是“真实脱敏、合成样例还是公开项目”？
- 每个核心 claim 是否标了 `Fact`、`Inference`、`Unverified`、`Private` 或 `Stop`？
- 是否把用户原话、PR、命令、log、final report 或 review comment 留成可复核证据，而不是只保留 AI 总结？
- 是否删除了无证据的收益数字、转化率、事故率和客户画像？
- 是否确认公开边界；如果没有确认，是否降级为方法样板或停止发布？
- 是否用 `Continue / Narrow / Stop` 收口，并写出下一步第一条证据动作？
