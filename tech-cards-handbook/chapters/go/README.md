# Go 技术卡片

本目录按"一张卡片一个 Markdown 文件"维护，共 13 张。文件名使用英文 `kebab-case`。

| 卡片 | 文件 |
|---|---|
| `sync.WaitGroup` 等待一组 goroutine 完成 | [`sync-waitgroup-goroutine-completion.md`](sync-waitgroup-goroutine-completion.md) |
| `context.Context` 传递取消信号,不传业务参数 | [`context-cancellation-not-business-data.md`](context-cancellation-not-business-data.md) |
| channel 的关闭权属于发送方 | [`channel-close-owned-by-sender.md`](channel-close-owned-by-sender.md) |
| Worker Pool 控制并发上限 | [`worker-pool-concurrency-limit.md`](worker-pool-concurrency-limit.md) |
| 生产者-消费者用 channel 传递所有权 | [`producer-consumer-channel-ownership.md`](producer-consumer-channel-ownership.md) |
| `select` 用来同时等待结果、超时和取消 | [`select-results-timeouts-cancellation.md`](select-results-timeouts-cancellation.md) |
| `sync.Mutex` 保护短小共享状态 | [`sync-mutex-short-shared-state.md`](sync-mutex-short-shared-state.md) |
| 错误要保留上下文 | [`errors-keep-context.md`](errors-keep-context.md) |
| 小接口由使用方定义 | [`small-interfaces-defined-by-consumer.md`](small-interfaces-defined-by-consumer.md) |
| 表格驱动测试让边界更清楚 | [`table-driven-tests-boundaries.md`](table-driven-tests-boundaries.md) |
| HTTP handler 不要把内部错误暴露给客户端 | [`http-handler-hides-internal-errors.md`](http-handler-hides-internal-errors.md) |
| HTTP handler 不直接绑定数据库模型 | [`http-handler-does-not-bind-database-model.md`](http-handler-does-not-bind-database-model.md) |
| 请求 JSON 不直接反序列化到数据库 row | [`request-json-does-not-decode-into-database-row.md`](request-json-does-not-decode-into-database-row.md) |

## 边界实践阅读线

Go 代码的边界问题通常先出现在并发所有权，再进入取消、接口、错误和 HTTP adapter。建议按下面顺序复习：

1. **并发生命周期**：先读 `sync.WaitGroup`、worker pool、`select` 三张卡片，明确 goroutine 何时开始、何时结束、谁负责等待。
2. **channel 所有权**：再读 channel 关闭权和生产者-消费者两张卡片，确认“谁发送、谁关闭、谁消费”不会混在一起。
3. **取消边界**：用 `context.Context` 卡片复核取消信号只表达生命周期，不夹带业务参数。
4. **接口边界**：用“小接口由使用方定义”卡片把依赖反转到调用方，避免把实现细节扩散到业务层。
5. **错误与 adapter 边界**：最后连读“错误要保留上下文”、“HTTP handler 不要把内部错误暴露给客户端”、“HTTP handler 不直接绑定数据库模型”和“请求 JSON 不直接反序列化到数据库 row”，做到内部日志可诊断、外部响应可安全、输入 DTO 与存储模型不互相污染。

快速自检：一个函数如果同时负责启动 goroutine、关闭 channel、解析 HTTP 请求、访问数据库并决定响应格式，通常已经跨越太多边界，应先拆出 worker、service、handler 和 DTO / command mapper。

## 可运行验证进度

Go 工具链已在本机确认可用(`go version`)。当前优先把示例改成可复制运行的小程序;新增或改写卡片时,至少补一个 `go run <file>.go` 或 `go test` 的检查命令。

批量复核命令:

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
| [`http-handler-hides-internal-errors.md`](http-handler-hides-internal-errors.md) | `go run http-handler-hides-internal-errors.go` |
| [`http-handler-does-not-bind-database-model.md`](http-handler-does-not-bind-database-model.md) | `go run http-handler-does-not-bind-database-model.go` |
| [`request-json-does-not-decode-into-database-row.md`](request-json-does-not-decode-into-database-row.md) | `go run request-json-does-not-decode-into-database-row.go` |
