# AI Agent 最佳实践指南：章节索引

> 从概念到生产：构建智能、可靠、可扩展的 AI Agent 系统。

## 目录

| 章节 | 文件 | 主题 |
|---|---|---|
| 1 | `01-introduction.md` | Agent 基础概念、核心组成和第一个最小示例 |
| 2 | `02-design-principles.md` | 好 Agent 的特征、设计原则和常见陷阱 |
| 3 | `03-tech-stack.md` | LLM、框架、工具和基础设施选型 |
| 4 | `04-single-agent-architecture.md` | ReAct、反思、Plan-and-Execute、记忆增强架构 |
| 5 | `05-multi-agent-systems.md` | 多 Agent 协作模式、设计原则、成本和协调 |
| 6 | `06-memory-system-design.md` | 短期记忆、长期记忆、向量检索和记忆维护 |
| 7 | `07-tool-integration.md` | 工具定义、执行安全、工具选择与路由 |
| 8 | `08-testing-debugging.md` | 测试分层、离线评估、权限测试和 trace 调试 |
| 9 | `09-deployment-monitoring.md` | 部署形态、可观测性、告警止损、弹性和回滚 |
| 10 | `10-safety-ethics.md` | 风险分级、权限网关、Prompt 注入防御、数据安全、人工审批、审计响应和伦理边界 |

## 阅读建议

1. 新手按章节顺序阅读，先建立 Agent 的基本概念和设计原则。
2. 已有开发经验的读者可以从第 4-7 章进入架构和工具集成。
3. 准备上线生产系统时，重点阅读第 8-10 章，并按“测试集 → 监控告警 → 安全门禁 → 熔断恢复”的顺序落地。

## 生产上线阅读路径

- 第 7 章：确认工具注册、工具描述、执行沙箱、权限边界和工具路由。
- 第 8 章：把关键任务写成 Golden Tasks，覆盖成功路径、失败路径、权限测试和 trace 调试。
- 第 9 章：建立部署、监控、告警、灰度、回滚和成本止损机制。
- 第 10 章：补齐 Prompt 注入防御、数据脱敏、人工审批、审计 trace、事故响应 runbook 与发布前安全检查清单。
