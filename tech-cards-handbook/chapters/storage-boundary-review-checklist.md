# 跨栈存储边界审查清单

> 这份清单把 Go handler / DTO 卡片和 Rust newtype / repository 卡片串成一次可执行的代码审查。适用于审查 CRUD、后台管理、API handler、repository adapter、ORM model 和导入脚本。

## 使用方法

1. 打开要审查的一个用例，例如“更新用户资料”或“创建订单”。
2. 先画出四列：`输入 DTO`、`领域 command/model`、`存储 row`、`输出 DTO`。
3. 按下面五个检查点逐项过；任意一列直接复制另一列字段、错误语义或类型时，都要补 mapper / newtype / 显式转换。
4. 把不符合项写入底部复审输出表，按优先级修复。

---

## 检查 1：外部输入是否先进入 DTO / command？

| 问题 | 是 | 否 |
|---|---|---|
| HTTP JSON、消息载荷或表单是否先进入 request DTO，而不是直接 decode 到数据库 row / ORM model？ | | |
| 客户端可提交字段是否被白名单化，避免提交 `role`、`passwordHash`、`deletedAt`、内部状态等字段？ | | |
| DTO 到 command 的 mapper 是否执行了 trim、默认值、枚举归一化等边界处理？ | | |

**深度阅读：**
- Go: [`go/request-json-does-not-decode-into-database-row.md`](go/request-json-does-not-decode-into-database-row.md)

---

## 检查 2：领域概念是否有自己的类型？

| 问题 | 是 | 否 |
|---|---|---|
| 业务函数签名里是否避免连续出现多个同类型裸值（如多个 `String` / `u64` / `bool`）？ | | |
| `UserId`、`OrderId`、`EmailAddress`、`Money`、状态枚举等概念是否有领域类型表达？ | | |
| 领域类型是否控制构造入口，避免任意层随手拼出非法状态？ | | |

**深度阅读：**
- Rust: [`rust/newtype-separates-domain-from-primitive.md`](rust/newtype-separates-domain-from-primitive.md)

---

## 检查 3：跨边界转换是否可失败？

| 问题 | 是 | 否 |
|---|---|---|
| 外部输入、数据库字段、消息载荷进入领域类型时是否使用 `TryFrom` / `FromStr` / `new(...) -> Result<_, _>`？ | | |
| 是否避免用 `From` / `Into` 表达可能失败的业务验证？ | | |
| 验证是否靠近边界发生一次，而不是在业务流程里重复散落同一条规则？ | | |

**深度阅读：**
- Rust: [`rust/from-into-do-not-skip-validation-boundary.md`](rust/from-into-do-not-skip-validation-boundary.md)

---

## 检查 4：repository 是否只暴露领域语言？

| 问题 | 是 | 否 |
|---|---|---|
| repository trait / interface 的公开签名是否返回领域模型，而不是 `Row`、`Record`、`EntityModel`、`serde_json::Value`？ | | |
| SQL row、ORM model、列名、分页游标实现细节是否被限制在 adapter 内部？ | | |
| driver error / SQL state 是否在 adapter 层翻译成领域错误，而不是让 service / handler 决策？ | | |

**深度阅读：**
- Rust: [`rust/repository-does-not-leak-database-row.md`](rust/repository-does-not-leak-database-row.md)

---

## 检查 5：handler 输出是否显式挑选公开字段？

| 问题 | 是 | 否 |
|---|---|---|
| 响应是否由 output DTO / presenter 生成，而不是直接序列化数据库模型或领域内部结构？ | | |
| password hash、软删除标记、内部时间戳、权限字段、存储枚举是否不会出现在公开响应里？ | | |
| 内部错误上下文是否只进日志，对外响应只包含稳定错误码和用户可理解消息？ | | |

**深度阅读：**
- Go: [`go/http-handler-does-not-bind-database-model.md`](go/http-handler-does-not-bind-database-model.md)
- Go: [`go/http-handler-hides-internal-errors.md`](go/http-handler-hides-internal-errors.md)

---

## 复审输出模板

完成检查后，把不符合项填入下表：

| 检查点 | 不符合描述 | 涉及文件 | 修复方案 | 优先级 |
|---|---|---|---|---|
| | | | | |

优先级参考：
- **P0**: 客户端可写内部权限字段、公开响应泄漏密码 hash / 删除标记 / 内部错误细节 → 立即修复。
- **P1**: handler / service / repository 公开签名泄漏数据库 row、ORM model 或 SQL state → 本迭代修复。
- **P2**: 领域概念仍是裸 `String` / `u64` / `bool`，容易参数错位或非法状态流入 → 重构时补 newtype 和构造验证。
- **P3**: mapper 命名、表格化复审输出或测试覆盖不足 → 后续迭代补齐。
