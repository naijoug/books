# Rust 技术卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 13 张。文件名使用英文 `kebab-case`。

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

## 可运行验证进度

Rust 工具链已在本机确认可用（`rustc --version`）。当前优先把示例改成可复制运行的小程序；新增或改写卡片时，至少补一个 `rustc <file>.rs && ./<file>` 的检查命令。

批量复核可在 `books` 仓库根目录运行：`python3 scripts/verify_rust_cards.py --verbose`。该脚本会从下列 13 张卡片抽取唯一 `rust` 代码块，编译并运行；测试卡片会额外执行 `rustc --test`。

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
