# Rust 技术卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 16 张。文件名使用英文 `kebab-case`。

| 卡片 | 文件 |
|---|---|
| 所有权解决“谁负责释放资源” | [`ownership-resource-release.md`](ownership-resource-release.md) |
| 借用用于临时读取或修改 | [`borrowing-temporary-read-write.md`](borrowing-temporary-read-write.md) |
| `Option` 表达“可能没有” | [`option-means-maybe-none.md`](option-means-maybe-none.md) |
| `Result` 表达“可能失败且有原因” | [`result-means-failable-with-reason.md`](result-means-failable-with-reason.md) |
| trait 表达行为契约 | [`trait-behavior-contract.md`](trait-behavior-contract.md) |
| 生命周期标注描述引用关系 | [`lifetimes-describe-reference-relations.md`](lifetimes-describe-reference-relations.md) |
| 模式匹配让分支覆盖更可靠 | [`pattern-matching-exhaustive-branches.md`](pattern-matching-exhaustive-branches.md) |
| 模块边界控制可见性 | [`modules-control-visibility.md`](modules-control-visibility.md) |
| 迭代器让数据转换更可组合 | [`iterators-composable-transformations.md`](iterators-composable-transformations.md) |
| 并发共享数据优先用消息或锁 | [`concurrency-message-or-lock.md`](concurrency-message-or-lock.md) |
| 异步不是自动并行 | [`async-is-not-parallel.md`](async-is-not-parallel.md) |
| 测试要覆盖成功路径和失败路径 | [`tests-cover-success-and-failure.md`](tests-cover-success-and-failure.md) |
| newtype 把领域概念从原始类型里拆出来 | [`newtype-separates-domain-from-primitive.md`](newtype-separates-domain-from-primitive.md) |
| derive 不等于自动正确 | [`derive-does-not-mean-automatic-correctness.md`](derive-does-not-mean-automatic-correctness.md) |
| From/Into 不要跨越业务验证边界 | [`from-into-do-not-skip-validation-boundary.md`](from-into-do-not-skip-validation-boundary.md) |
| Repository 不要把数据库 row 泄漏到领域层 | [`repository-does-not-leak-database-row.md`](repository-does-not-leak-database-row.md) |

## 领域建模阅读线

如果目标是用 Rust 写出更难误用的领域代码，可以按这条线复习：

1. **所有权边界**：先读 [`ownership-resource-release.md`](ownership-resource-release.md) 和 [`borrowing-temporary-read-write.md`](borrowing-temporary-read-write.md)，确认资源由谁拥有、函数只临时读取还是会修改。
2. **缺失与失败边界**：再读 [`option-means-maybe-none.md`](option-means-maybe-none.md) 和 [`result-means-failable-with-reason.md`](result-means-failable-with-reason.md)，把“没有”和“失败”显式写进返回类型，而不是靠空字符串、零值或 panic 暗示。
3. **行为与可见性边界**：接着读 [`trait-behavior-contract.md`](trait-behavior-contract.md)、[`lifetimes-describe-reference-relations.md`](lifetimes-describe-reference-relations.md) 和 [`modules-control-visibility.md`](modules-control-visibility.md)，让外部依赖行为契约和公开 API，而不是依赖结构体内部细节。
4. **领域类型边界**：读 [`newtype-separates-domain-from-primitive.md`](newtype-separates-domain-from-primitive.md)、[`from-into-do-not-skip-validation-boundary.md`](from-into-do-not-skip-validation-boundary.md) 和 [`repository-does-not-leak-database-row.md`](repository-does-not-leak-database-row.md)，把 `UserId`、`OrderId`、`EmailAddress` 这类概念从 `String` / `u64` / 数据库 row 里拆出来，并确认外部输入与持久化数据必须经过 `TryFrom` / `FromStr` / `new(...) -> Result<_, _>` 验证后才能进入领域类型。
5. **trait 语义承诺**：最后读 [`derive-does-not-mean-automatic-correctness.md`](derive-does-not-mean-automatic-correctness.md) 和 [`tests-cover-success-and-failure.md`](tests-cover-success-and-failure.md)，逐个确认 `Debug`、`Clone`、`Copy`、`PartialEq`、`From`、`Into` 是否真符合业务语义，并用成功/失败测试固定边界。

快速自检：如果一个函数签名里连续出现多个同类型原始值、repository trait 返回 `UserRow` / `Record`，返回值靠注释区分错误原因，`impl From<...> for DomainType` 可能绕过验证，或者 `#[derive(...)]` 暴露了还没讨论过的行为，就先停下来补领域类型、显式结果和最小测试。

## 存储边界阅读组

当你要把 Rust 用在真实业务服务里，可以把下面几张卡片连成一次 30 分钟的“存储边界”复盘：

1. [`newtype-separates-domain-from-primitive.md`](newtype-separates-domain-from-primitive.md)：先确认领域层不直接传 `String`、`u64`、`bool` 这类裸值，避免参数顺序和语义被调用方猜测。
2. [`from-into-do-not-skip-validation-boundary.md`](from-into-do-not-skip-validation-boundary.md)：再确认外部输入、数据库字段、消息载荷进入领域类型时使用 `TryFrom` / `FromStr` / `new(...) -> Result<_, _>`，不要用 `From` 假装转换永远安全。
3. [`repository-does-not-leak-database-row.md`](repository-does-not-leak-database-row.md)：最后检查 repository trait 是否只暴露领域模型与领域错误，`UserRow`、`sqlx::Row`、ORM model、分页游标细节是否都被关在 adapter 内部。

复盘时可以直接问三个问题：

- **签名是否泄漏存储实现？** 如果 trait、service 或 handler 的公开签名里出现 `Row`、`Record`、`EntityModel`、`serde_json::Value`，先把它们移回 adapter。
- **验证是否只发生一次且靠近边界？** 数据库读出的值和外部请求一样不可信；进入领域模型前要经过可失败转换，转换后不要在业务函数里反复检查同一条规则。
- **错误是否能被调用方理解？** 公开错误应该说“用户不存在”“邮箱无效”“状态不可迁移”，而不是直接冒出 SQL 状态码、列名或驱动错误。

这组卡片的目标不是反对 ORM 或 query builder，而是让 ORM 只负责持久化映射；业务代码依赖的是稳定的领域语言。完成后可回到 Go 章节的 `http-handler-does-not-bind-database-model.md` 和 `request-json-does-not-decode-into-database-row.md`，对照两种语言如何处理同一个边界问题。

## 可运行验证进度

Rust 工具链已在本机确认可用（`rustc --version`）。当前优先把示例改成可复制运行的小程序；新增或改写卡片时，至少补一个 `rustc <file>.rs && ./<file>` 的检查命令。

批量复核可在 `books` 仓库根目录运行：`python3 scripts/verify_rust_cards.py --verbose`。该脚本会从下列 16 张卡片抽取唯一 `rust` 代码块，编译并运行；测试卡片会额外执行 `rustc --test`。

| 卡片 | 验证方式 |
|---|---|
| [`ownership-resource-release.md`](ownership-resource-release.md) | `rustc ownership-resource-release.rs && ./ownership-resource-release` |
| [`borrowing-temporary-read-write.md`](borrowing-temporary-read-write.md) | `rustc borrowing-temporary-read-write.rs && ./borrowing-temporary-read-write` |
| [`option-means-maybe-none.md`](option-means-maybe-none.md) | `rustc option-means-maybe-none.rs && ./option-means-maybe-none` |
| [`result-means-failable-with-reason.md`](result-means-failable-with-reason.md) | `rustc result-means-failable-with-reason.rs && ./result-means-failable-with-reason` |
| [`trait-behavior-contract.md`](trait-behavior-contract.md) | `rustc trait-behavior-contract.rs && ./trait-behavior-contract` |
| [`lifetimes-describe-reference-relations.md`](lifetimes-describe-reference-relations.md) | `rustc lifetimes-describe-reference-relations.rs && ./lifetimes-describe-reference-relations` |
| [`pattern-matching-exhaustive-branches.md`](pattern-matching-exhaustive-branches.md) | `rustc pattern-matching-exhaustive-branches.rs && ./pattern-matching-exhaustive-branches` |
| [`modules-control-visibility.md`](modules-control-visibility.md) | `rustc modules-control-visibility.rs && ./modules-control-visibility` |
| [`iterators-composable-transformations.md`](iterators-composable-transformations.md) | `rustc iterators-composable-transformations.rs && ./iterators-composable-transformations` |
| [`concurrency-message-or-lock.md`](concurrency-message-or-lock.md) | `rustc concurrency-message-or-lock.rs && ./concurrency-message-or-lock` |
| [`async-is-not-parallel.md`](async-is-not-parallel.md) | `rustc --edition=2021 async-is-not-parallel.rs && ./async-is-not-parallel` |
| [`tests-cover-success-and-failure.md`](tests-cover-success-and-failure.md) | `rustc --test tests-cover-success-and-failure.rs && ./tests-cover-success-and-failure` |
| [`newtype-separates-domain-from-primitive.md`](newtype-separates-domain-from-primitive.md) | `rustc newtype-separates-domain-from-primitive.rs && ./newtype-separates-domain-from-primitive` |
| [`derive-does-not-mean-automatic-correctness.md`](derive-does-not-mean-automatic-correctness.md) | `rustc derive-does-not-mean-automatic-correctness.rs && ./derive-does-not-mean-automatic-correctness` |
| [`from-into-do-not-skip-validation-boundary.md`](from-into-do-not-skip-validation-boundary.md) | `rustc from-into-do-not-skip-validation-boundary.rs && ./from-into-do-not-skip-validation-boundary` |
| [`repository-does-not-leak-database-row.md`](repository-does-not-leak-database-row.md) | `rustc repository-does-not-leak-database-row.rs && ./repository-does-not-leak-database-row` |
