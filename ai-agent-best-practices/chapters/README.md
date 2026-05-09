# AI Agent 最佳实践指南：章节索引

> 从概念到生产：构建智能、可靠、可扩展的 AI Agent 系统。

## 目录

| 章节 | 文件 | 主题 |
|---|---|---|
| 1 | `01-introduction.md` | Agent 基础概念、核心组成和第一个最小示例 |
| 2 | `02-design-principles.md` | 好 Agent 的特征、设计原则和常见陷阱 |
| 3 | `03-tech-stack.md` | LLM、框架、工具和基础设施选型 |
| 4 | `04-single-agent-architecture.md` | ReAct、反思、Plan-and-Execute、记忆增强架构 |
| 5 | `05-multi-agent-systems.md` | 多 Agent 协作模式、设计原则和框架选择 |
| 6 | `06-memory-system-design.md` | 短期记忆、长期记忆、向量检索和记忆维护 |
| 7 | `07-tool-integration.md` | 工具定义、执行安全、工具选择与路由 |
| 8 | `08-testing-debugging.md` | 单元测试、集成测试、端到端测试和调试方法 |
| 9 | `09-deployment-monitoring.md` | 部署架构、可观测性、告警、弹性和容错 |
| 10 | `10-safety-ethics.md` | 安全风险、伦理边界、输入验证、人工确认和审计 |

## 阅读建议

1. 新手按章节顺序阅读，先建立 Agent 的基本概念和设计原则。
2. 已有开发经验的读者可以从第 4-7 章进入架构和工具集成。
3. 准备上线生产系统时，重点阅读第 8-10 章。

## 后续完善方向

1. 为每章补充统一的“本章目标”和“本章小结”。
2. 统一代码示例依赖、环境变量和运行方式。
3. 增加一个贯穿全书的示例 Agent 项目。
4. 第一章示例已更新为 LangChain v1 `create_agent` 风格；继续对其余章节的框架、模型和 API 名称进行事实核验。
