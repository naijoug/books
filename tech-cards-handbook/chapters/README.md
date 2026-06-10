# 技术卡片随身宝典：技术栈索引

正式内容按技术栈分目录维护；每张卡片是一个独立 Markdown 文件。

## 阅读方式

1. 先进入对应技术栈目录。
2. 按目录 README 的列表顺序阅读。
3. 遇到具体问题时，直接打开对应卡片。

## 技术栈目录

| 技术栈 | 目录 | 卡片数 |
|---|---|---|
| Python 技术卡片 | [`python/`](python/) | 18 |
| Go 技术卡片 | [`go/`](go/) | 14 |
| Rust 技术卡片 | [`rust/`](rust/) | 16 |
| TypeScript 技术卡片 | [`typescript/`](typescript/) | 26 |
| React 技术卡片 | [`react/`](react/) | 54 |
| Swift 技术卡片 | [`swift/`](swift/) | 10 |
| Flutter 技术卡片 | [`flutter/`](flutter/) | 10 |
| AI Agent 系统实践卡片 | [`ai-agent/`](ai-agent/) | 21 |

## 跨技术栈复盘路径

当一个问题已经在多个技术栈里反复出现，优先按“边界问题”而不是“语言特性”来复盘：

### 存储与 adapter 边界

这条路径适合审查 CRUD、后台管理、API handler 和 repository 代码，目标是防止外部契约、领域模型和数据库 row 相互泄漏。

1. **输入边界**：先读 Go 的 [`go/request-json-does-not-decode-into-database-row.md`](go/request-json-does-not-decode-into-database-row.md)，确认请求 JSON 只进入 request DTO / command，不直接写进数据库 row。
2. **handler 输出边界**：再读 Go 的 [`go/http-handler-does-not-bind-database-model.md`](go/http-handler-does-not-bind-database-model.md) 和 [`go/http-handler-hides-internal-errors.md`](go/http-handler-hides-internal-errors.md)，确认 handler 不透传存储字段、内部错误和日志上下文。
3. **领域类型边界**：切到 Rust 的 [`rust/newtype-separates-domain-from-primitive.md`](rust/newtype-separates-domain-from-primitive.md) 与 [`rust/from-into-do-not-skip-validation-boundary.md`](rust/from-into-do-not-skip-validation-boundary.md)，检查 `UserId`、`EmailAddress`、状态枚举这类概念是否先经过可失败验证再进入业务层。
4. **repository 边界**：最后读 Rust 的 [`rust/repository-does-not-leak-database-row.md`](rust/repository-does-not-leak-database-row.md)，确认 repository trait 只暴露领域模型和领域错误，ORM model / SQL row / driver error 被限制在 adapter 内。

复盘输出可以是一张四列表：`输入 DTO`、`领域 command/model`、`存储 row`、`输出 DTO`。如果任意一列的字段名、错误语义或类型直接复制到另一列，就要补 mapper、newtype 或显式错误转换。

### 错误传播与分类边界

这条路径适合审查 service、repository、handler 和 CLI command 的错误返回，目标是让错误既能保留诊断上下文，又能被调用方稳定分类处理。

1. **先确认失败是否进入类型系统**：读 Rust 的 [`rust/result-means-failable-with-reason.md`](rust/result-means-failable-with-reason.md)，把“可能失败且有原因”写进返回类型，而不是用空值、布尔值或 panic 暗示。
2. **再确认上下文没有断链**：读 Go 的 [`go/errors-keep-context.md`](go/errors-keep-context.md)，检查每一层是否用 `%w` 保留根因，并补上“做什么、对谁做”的上下文。
3. **最后做跨语言对照**：读 Go 的 [`go/error-wrapping-vs-result-propagation.md`](go/error-wrapping-vs-result-propagation.md)，比较 Go 的 `errors.Is` / `errors.As` 与 Rust 的 `From` / `?` / `match`，确认调用方能区分重试、降级、用户可见错误和内部故障。

复盘输出可以是一张四列表：`底层错误`、`领域错误`、`调用方动作`、`对外消息`。如果上层需要知道 SQL 状态码、文件系统错误码或第三方 SDK 类型才能决策，就要在 adapter 边界补领域错误转换；如果对外消息直接拼接底层错误字符串，就要拆出日志上下文和用户可见错误码。

## 卡片维护规则

- 新卡片放入对应技术栈目录，文件名使用英文 `kebab-case`，不要使用纯数字命名。
- 每张正式卡片必须包含“问题、要点、示例、坑、检查”。
- 长教程、原始素材和未定稿片段不要直接放入正式卡片；先提炼成单一问题。
- 目录优先按具体技术栈命名，避免使用“前端”“移动端”这类领域混合桶。
- 跨技术栈内容优先放在主要实践场景所在目录，并在相关目录 README 中交叉引用。
- Agent 系统设计、工具、记忆和心跳工作流放入 `ai-agent/`；具体 SDK 或语言实现优先放入对应技术栈目录。
