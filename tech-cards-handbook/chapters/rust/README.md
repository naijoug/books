# Rust 技术卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 12 张。文件名使用英文 `kebab-case`。

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
