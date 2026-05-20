# Go 技术卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 10 张。文件名使用英文 `kebab-case`。

| 卡片 | 文件 |
|---|---|
| `sync.WaitGroup` 等待一组 goroutine 完成 | [`sync-waitgroup-goroutine-completion.md`](sync-waitgroup-goroutine-completion.md) |
| `context.Context` 传递取消信号，不传业务参数 | [`context-cancellation-not-business-data.md`](context-cancellation-not-business-data.md) |
| channel 的关闭权属于发送方 | [`channel-close-owned-by-sender.md`](channel-close-owned-by-sender.md) |
| Worker Pool 控制并发上限 | [`worker-pool-concurrency-limit.md`](worker-pool-concurrency-limit.md) |
| 生产者-消费者用 channel 传递所有权 | [`producer-consumer-channel-ownership.md`](producer-consumer-channel-ownership.md) |
| `select` 用来同时等待结果、超时和取消 | [`select-results-timeouts-cancellation.md`](select-results-timeouts-cancellation.md) |
| `sync.Mutex` 保护短小共享状态 | [`sync-mutex-short-shared-state.md`](sync-mutex-short-shared-state.md) |
| 错误要保留上下文 | [`errors-keep-context.md`](errors-keep-context.md) |
| 小接口由使用方定义 | [`small-interfaces-defined-by-consumer.md`](small-interfaces-defined-by-consumer.md) |
| 表格驱动测试让边界更清楚 | [`table-driven-tests-boundaries.md`](table-driven-tests-boundaries.md) |
