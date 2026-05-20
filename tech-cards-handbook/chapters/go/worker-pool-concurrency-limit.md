# Worker Pool 控制并发上限

**问题**：有 10000 个任务，如何避免一次性启动 10000 个 goroutine 打爆下游？

**要点**：

- 固定 worker 数量。
- jobs channel 负责分发任务。
- results 或 error channel 汇总结果。

**示例**：

```go
func worker(ctx context.Context, jobs <-chan Job, results chan<- Result) {
	for {
		select {
		case <-ctx.Done():
			return
		case job, ok := <-jobs:
			if !ok {
				return
			}
			results <- process(job)
		}
	}
}
```

**坑**：只限制 goroutine 数量不够，还要考虑数据库连接池、API 限流和内存占用。

**检查**：worker 数是否来自下游容量，而不是拍脑袋的 CPU 核数。
