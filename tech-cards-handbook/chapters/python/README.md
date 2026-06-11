# Python 技术卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 19 张。文件名使用英文 `kebab-case`。

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
| 自定义异常层级让错误可分类 | [`custom-exception-hierarchy-makes-errors-classifiable.md`](custom-exception-hierarchy-makes-errors-classifiable.md) |

## 可运行验证索引

当前 19 张 Python 卡片都带有可复制的验证命令。维护原则：新增或改写卡片时，至少保留一个能在本地失败/通过的检查；优先使用标准库和无网络依赖，只有测试框架或静态检查确有价值时才引入外部工具。

批量复核命令：

```bash
python3 scripts/verify_python_cards.py
```

脚本会从本目录 README 读取 19 张卡片，逐张抽取唯一 `python` 代码块并运行；测试卡片通过 `uv run --with pytest` 执行，类型卡片会额外运行 `npx -y pyright@1.1.407`。

| 类型 | 卡片 | 验证方式 |
|---|---|---|
| 异步基础 | [`asyncio-reduces-waiting.md`](asyncio-reduces-waiting.md) | `python3 asyncio-reduces-waiting.py` |
| 异步基础 | [`asyncio-run-sync-entrypoint.md`](asyncio-run-sync-entrypoint.md) | `python3 asyncio-run-sync-entrypoint.py` |
| 异步批量 | [`asyncio-gather-batch-io.md`](asyncio-gather-batch-io.md) | `python3 asyncio-gather-batch-io.py` |
| 异步批量 | [`semaphore-limits-async-concurrency.md`](semaphore-limits-async-concurrency.md) | `python3 semaphore-limits-async-concurrency.py` |
| 异步共享状态 | [`asyncio-lock-shared-state.md`](asyncio-lock-shared-state.md) | `python3 asyncio-lock-shared-state.py` |
| 异步队列 | [`queue-decouples-producers-consumers.md`](queue-decouples-producers-consumers.md) | `python3 queue-decouples-producers-consumers.py` |
| 异步同步原语 | [`event-one-shot-broadcast.md`](event-one-shot-broadcast.md) | `python3 event-one-shot-broadcast.py` |
| 异步同步原语 | [`condition-complex-state-changes.md`](condition-complex-state-changes.md) | `python3 condition-complex-state-changes.py` |
| 异步生命周期 | [`taskgroup-shared-lifecycle.md`](taskgroup-shared-lifecycle.md) | `python3.11 taskgroup-shared-lifecycle.py` |
| 异步生命周期 | [`task-cancellation-cleanup.md`](task-cancellation-cleanup.md) | `python3 task-cancellation-cleanup.py` |
| 异步边界 | [`timeout-async-system-boundary.md`](timeout-async-system-boundary.md) | `python3 timeout-async-system-boundary.py` |
| 语言机制 | [`context-manager-enter-exit-boundary.md`](context-manager-enter-exit-boundary.md) | `python3 context-manager-enter-exit-boundary.py` |
| 语言机制 | [`generators-for-streaming.md`](generators-for-streaming.md) | `python3 generators-for-streaming.py` |
| 装饰器 | [`decorators-wrap-behavior.md`](decorators-wrap-behavior.md) | `python3 decorators-wrap-behavior.py` |
| 装饰器 | [`decorators-for-timing-and-auth.md`](decorators-for-timing-and-auth.md) | `python3 decorators-for-timing-and-auth.py` |
| 装饰器 | [`parameterized-decorator-extra-layer.md`](parameterized-decorator-extra-layer.md) | `python3 parameterized-decorator-extra-layer.py` |
| 类型契约 | [`type-hints-express-contracts.md`](type-hints-express-contracts.md) | `python3 type-hints-express-contracts.py` + `npx -y pyright@1.1.407 type-hints-express-contracts.py` |
| 测试策略 | [`tests-cover-behavior-first.md`](tests-cover-behavior-first.md) | `uv run --with pytest python -m pytest -q tests-cover-behavior-first.py` |
| 错误分类 | [`custom-exception-hierarchy-makes-errors-classifiable.md`](custom-exception-hierarchy-makes-errors-classifiable.md) | `python3 custom-exception-hierarchy-makes-errors-classifiable.py` |
