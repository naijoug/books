# Rust 技术卡片

本目录按"一张卡片一个 Markdown 文件"维护，共 19 张。文件名使用英文 `kebab-case`。

| 卡片 | 文件 |
|---|---|
| 所有权解决"谁负责释放资源" | [`ownership-resource-release.md`](ownership-resource-release.md) |
| 借用用于临时读取或修改 | [`borrowing-temporary-read-write.md`](borrowing-temporary-read-write.md) |
| `Option` 表达"可能没有" | [`option-means-maybe-none.md`](option-means-maybe-none.md) |
| `Result` 表达"可能失败且有原因" | [`result-means-failable-with-reason.md`](result-means-failable-with-reason.md) |
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
| 错误恢复要用显式重试策略，而不是在错误处理里循环 | [`retry-strategy-explicit-not-implicit-loop.md`](retry-strategy-explicit-not-implicit-loop.md) |
| 对外错误码应由领域定义，而不是从基础设施泄漏 | [`external-error-codes-domain-defined-not-leaked.md`](external-error-codes-domain-defined-not-leaked.md) |
| 降级策略要在调用方实现，而不是在被调方隐藏 | [`degradation-strategy-at-caller-not-callee.md`](degradation-strategy-at-caller-not-callee.md) |

## 领域建模阅读线

如果目标是用 Rust 写出更难误用的领域代码,可以按这条线复习:

1. **所有权边界**:先读 [`ownership-resource-release.md`](ownership-resource-release.md) 和 [`borrowing-temporary-read-write.md`](borrowing-temporary-read-write.md),确认资源由谁拥有、函数只临时读取还是会修改。
2. **缺失与失败边界**:再读 [`option-means-maybe-none.md`](option-means-maybe-none.md) 和 [`result-means-failable-with-reason.md`](result-means-failable-with-reason.md),把"没有"和"失败"显式写进返回类型,而不是靠空字符串、零值或 panic 暗示。
3. **行为与可见性边界**:接着读 [`trait-behavior-contract.md`](trait-behavior-contract.md)、[`lifetimes-describe-reference-relations.md`](lifetimes-describe-reference-relations.md) 和 [`modules-control-visibility.md`](modules-control-visibility.md),让外部依赖行为契约和公开 API,而不是依赖结构体内部细节。
4. **领域类型边界**:读 [`newtype-separates-domain-from-primitive.md`](newtype-separates-domain-from-primitive.md)、[`from-into-do-not-skip-validation-boundary.md`](from-into-do-not-skip-validation-boundary.md) 和 [`repository-does-not-leak-database-row.md`](repository-does-not-leak-database-row.md),把 `UserId`、`OrderId`、`EmailAddress` 这类概念从 `String` / `u64` / 数据库 row 里拆出来,并确认外部输入与持久化数据必须经过 `TryFrom` / `FromStr` / `new(...) -> Result<_, _>` 验证后才能进入领域类型。
5. **trait 语义承诺**:最后读 [`derive-does-not-mean-automatic-correctness.md`](derive-does-not-mean-automatic-correctness.md) 和 [`tests-cover-success-and-failure.md`](tests-cover-success-and-failure.md),逐个确认 `Debug`、`Clone`、`Copy`、`PartialEq`、`From`、`Into` 是否真符合业务语义,并用成功/失败测试固定边界。

快速自检:如果一个函数签名里连续出现多个同类型原始值、repository trait 返回 `UserRow` / `Record`,返回值靠注释区分错误原因,`impl From<...> for DomainType` 可能绕过验证,或者 `#[derive(...)]` 暴露了还没讨论过的行为,就先停下来补领域类型、显式结果和最小测试。

## 错误恢复阅读组

当你要审查一个会调用数据库、外部 API、文件系统或队列的 Rust service 时,可以把下面几张卡片连成一次"失败路径"复盘:

1. [`result-means-failable-with-reason.md`](result-means-failable-with-reason.md):先确认函数签名把失败原因写进 `Result<T, E>`,调用方不用靠空值、日志或 panic 猜测失败。
2. [`pattern-matching-exhaustive-branches.md`](pattern-matching-exhaustive-branches.md):再检查调用方是否穷尽处理领域错误,而不是用 `_ =>` 把可恢复、不可恢复、用户可见和内部错误混在一起。
3. [`retry-strategy-explicit-not-implicit-loop.md`](retry-strategy-explicit-not-implicit-loop.md)：把恢复动作显式化，确认可重试错误集合、最大次数、退避间隔和耗尽后的返回值都能被测试。
4. [`external-error-codes-domain-defined-not-leaked.md`](external-error-codes-domain-defined-not-leaked.md)：检查对外返回的错误码是否来自领域枚举，底层 SQL state、驱动类型名或内部错误字符串是否被 adapter 翻译成了稳定的领域错误码。
5. [`degradation-strategy-at-caller-not-callee.md`](degradation-strategy-at-caller-not-callee.md)：确认降级决策是在调用方根据业务语义做出，而不是被调方静默返回假结果。

复盘时可以直接问三个问题:

- **错误分类是否稳定?** 上层应该匹配领域错误枚举,而不是匹配数据库驱动、HTTP client 或 SDK 的内部错误类型。
- **恢复策略是否可配置、可测试?** 重试次数、退避间隔和是否允许降级不要散落在 `match` 分支里;用 `RetryPolicy`、配置项或显式函数参数表达。
- **失败耗尽后是否仍保留上下文?** 重试结束后返回的错误要保留"做什么、对谁做、最后一次失败原因",但对外消息不要直接泄露底层错误字符串。

这组卡片可以和 Go 章节的 `errors-keep-context.md`、`error-wrapping-vs-result-propagation.md` 对照阅读：Go 更依赖 `%w` / `errors.Is` 保留链路，Rust 更适合用错误枚举和 `match` 固定分类，但两者都需要把"恢复动作"从临时错误处理代码里拆出来。Go 对外错误码通常在 HTTP handler 层从 `%w` 链中提取领域状态码；Rust 则在 adapter 的 `map_err` 中把底层错误翻译成领域枚举——两者目标相同：调用方只看到领域错误码和用户可见描述。

## 存储边界阅读组

当你要把 Rust 用在真实业务服务里,可以把下面几张卡片连成一次 30 分钟的"存储边界"复盘:

1. [`newtype-separates-domain-from-primitive.md`](newtype-separates-domain-from-primitive.md):先确认领域层不直接传 `String`、`u64`、`bool` 这类裸值,避免参数顺序和语义被调用方猜测。
2. [`from-into-do-not-skip-validation-boundary.md`](from-into-do-not-skip-validation-boundary.md):再确认外部输入、数据库字段、消息载荷进入领域类型时使用 `TryFrom` / `FromStr` / `new(...) -> Result<_, _>`,不要用 `From` 假装转换永远安全。
3. [`repository-does-not-leak-database-row.md`](repository-does-not-leak-database-row.md):最后检查 repository trait 是否只暴露领域模型与领域错误,`UserRow`、`sqlx::Row`、ORM model、分页游标细节是否都被关在 adapter 内部。

复盘时可以直接问三个问题:

- **签名是否泄漏存储实现?** 如果 trait、service 或 handler 的公开签名里出现 `Row`、`Record`、`EntityModel`、`serde_json::Value`,先把它们移回 adapter。
- **验证是否只发生一次且靠近边界?** 数据库读出的值和外部请求一样不可信;进入领域模型前要经过可失败转换,转换后不要在业务函数里反复检查同一条规则。
- **错误是否能被调用方理解?** 公开错误应该说"用户不存在""邮箱无效""状态不可迁移",而不是直接冒出 SQL 状态码、列名或驱动错误。

这组卡片的目标不是反对 ORM 或 query builder,而是让 ORM 只负责持久化映射;业务代码依赖的是稳定的领域语言。完成后可回到 Go 章节的 `http-handler-does-not-bind-database-model.md` 和 `request-json-does-not-decode-into-database-row.md`,对照两种语言如何处理同一个边界问题。

## 可运行验证进度

Rust 工具链已在本机确认可用(`rustc --version`)。当前优先把示例改成可复制运行的小程序；新增或改写卡片时，至少补一个 `rustc <file>.rs && ./<file>` 的检查命令。

批量复核可在 `books` 仓库根目录运行：`python3 scripts/verify_rust_cards.py --verbose`。该脚本会从下列 18 张卡片抽取唯一 `rust` 代码块，编译并运行；测试卡片会额外执行 `rustc --test`。

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
| [`retry-strategy-explicit-not-implicit-loop.md`](retry-strategy-explicit-not-implicit-loop.md) | `rustc retry-strategy-explicit-not-implicit-loop.rs && ./retry-strategy-explicit-not-implicit-loop` |
| [`external-error-codes-domain-defined-not-leaked.md`](external-error-codes-domain-defined-not-leaked.md) | `rustc external-error-codes-domain-defined-not-leaked.rs && ./external-error-codes-domain-defined-not-leaked` |
| [`degradation-strategy-at-caller-not-callee.md`](degradation-strategy-at-caller-not-callee.md) | `rustc degradation-strategy-at-caller-not-callee.rs && ./degradation-strategy-at-caller-not-callee` |
