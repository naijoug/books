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

## 可运行验证进度

Go 工具链已在本机确认可用（`go version`）。当前优先把示例改成可复制运行的小程序；新增或改写卡片时，至少补一个 `go run <file>.go` 或 `go test` 的检查命令。

批量复核命令：

```bash
python3 scripts/verify_go_cards.py
```

| 卡片 | 验证方式 |
|---|---|
| [`sync-waitgroup-goroutine-completion.md`](sync-waitgroup-goroutine-completion.md) | `go run sync-waitgroup-goroutine-completion.go` |
| [`context-cancellation-not-business-data.md`](context-cancellation-not-business-data.md) | `go run context-cancellation-not-business-data.go` |
| [`channel-close-owned-by-sender.md`](channel-close-owned-by-sender.md) | `go run channel-close-owned-by-sender.go` |
| [`worker-pool-concurrency-limit.md`](worker-pool-concurrency-limit.md) | `go run worker-pool-concurrency-limit.go` |
| [`producer-consumer-channel-ownership.md`](producer-consumer-channel-ownership.md) | `go run producer-consumer-channel-ownership.go` |
| [`select-results-timeouts-cancellation.md`](select-results-timeouts-cancellation.md) | `go run select-results-timeouts-cancellation.go` |
| [`sync-mutex-short-shared-state.md`](sync-mutex-short-shared-state.md) | `go run sync-mutex-short-shared-state.go` |
| [`errors-keep-context.md`](errors-keep-context.md) | `go run errors-keep-context.go` |
| [`small-interfaces-defined-by-consumer.md`](small-interfaces-defined-by-consumer.md) | `go run small-interfaces-defined-by-consumer.go` |
| [`table-driven-tests-boundaries.md`](table-driven-tests-boundaries.md) | `go test email_test.go`（抽取为 `email_test.go`） |
