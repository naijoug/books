# Python 技术卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 18 张。文件名使用英文 `kebab-case`。

| 卡片 | 文件 |
|---|---|
| `asyncio` 不是让代码更快，而是减少等待浪费 | [`asyncio-reduces-waiting.md`](asyncio-reduces-waiting.md) |
| 取消任务时要让清理逻辑运行 | [`task-cancellation-cleanup.md`](task-cancellation-cleanup.md) |
| 上下文管理器用于固定“进入/退出”边界 | [`context-manager-enter-exit-boundary.md`](context-manager-enter-exit-boundary.md) |
| 生成器适合流式处理，不适合重复遍历 | [`generators-for-streaming.md`](generators-for-streaming.md) |
| 类型标注用于表达契约，不是替代测试 | [`type-hints-express-contracts.md`](type-hints-express-contracts.md) |
| 测试先覆盖行为，再覆盖实现细节 | [`tests-cover-behavior-first.md`](tests-cover-behavior-first.md) |
| `Semaphore` 限制同时运行的异步任务数 | [`semaphore-limits-async-concurrency.md`](semaphore-limits-async-concurrency.md) |
| `asyncio.Lock` 保护共享状态 | [`asyncio-lock-shared-state.md`](asyncio-lock-shared-state.md) |
| `Queue` 让生产者和消费者解耦 | [`queue-decouples-producers-consumers.md`](queue-decouples-producers-consumers.md) |
| `Event` 适合一次性广播通知 | [`event-one-shot-broadcast.md`](event-one-shot-broadcast.md) |
| `Condition` 用于等待复杂状态变化 | [`condition-complex-state-changes.md`](condition-complex-state-changes.md) |
| `TaskGroup` 让一组任务同生共死 | [`taskgroup-shared-lifecycle.md`](taskgroup-shared-lifecycle.md) |
| 超时是异步系统的基本边界 | [`timeout-async-system-boundary.md`](timeout-async-system-boundary.md) |
| `asyncio.run()` 是异步程序的同步入口 | [`asyncio-run-sync-entrypoint.md`](asyncio-run-sync-entrypoint.md) |
| `asyncio.gather` 适合批量等待同类 I/O | [`asyncio-gather-batch-io.md`](asyncio-gather-batch-io.md) |
| 装饰器是在不改调用方的情况下包一层行为 | [`decorators-wrap-behavior.md`](decorators-wrap-behavior.md) |
| 计时和权限检查适合做成装饰器 | [`decorators-for-timing-and-auth.md`](decorators-for-timing-and-auth.md) |
| 带参数装饰器需要再多一层函数 | [`parameterized-decorator-extra-layer.md`](parameterized-decorator-extra-layer.md) |
