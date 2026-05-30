# Worker Pool 控制并发上限

**问题**：有 10000 个任务，如何避免一次性启动 10000 个 goroutine 打爆下游？

**要点**：

- 固定 worker 数量，把“最多同时处理多少任务”变成显式容量。
- jobs channel 负责分发任务，所有任务入队后由发送方关闭。
- results 或 error channel 汇总结果，等待所有 worker 退出后再关闭结果通道。

**示例**：

```go
package main

import (
	"sort"
	"sync"
)

type Job struct {
	ID    int
	Value int
}

type Result struct {
	JobID int
	Value int
}

func worker(jobs <-chan Job, results chan<- Result, active *int, maxActive *int, mu *sync.Mutex, wg *sync.WaitGroup) {
	defer wg.Done()
	for job := range jobs {
		mu.Lock()
		*active++
		if *active > *maxActive {
			*maxActive = *active
		}
		mu.Unlock()

		results <- Result{JobID: job.ID, Value: job.Value * job.Value}

		mu.Lock()
		*active--
		mu.Unlock()
	}
}

func runPool(workerCount int, input []Job) ([]Result, int) {
	jobs := make(chan Job)
	results := make(chan Result, len(input))

	var wg sync.WaitGroup
	var mu sync.Mutex
	active := 0
	maxActive := 0

	for i := 0; i < workerCount; i++ {
		wg.Add(1)
		go worker(jobs, results, &active, &maxActive, &mu, &wg)
	}

	go func() {
		defer close(jobs)
		for _, job := range input {
			jobs <- job
		}
	}()

	go func() {
		wg.Wait()
		close(results)
	}()

	collected := make([]Result, 0, len(input))
	for result := range results {
		collected = append(collected, result)
	}

	return collected, maxActive
}

func main() {
	jobs := []Job{
		{ID: 1, Value: 2},
		{ID: 2, Value: 3},
		{ID: 3, Value: 4},
		{ID: 4, Value: 5},
		{ID: 5, Value: 6},
	}

	results, maxActive := runPool(2, jobs)
	if maxActive > 2 {
		panic("worker pool exceeded concurrency limit")
	}

	sort.Slice(results, func(i, j int) bool { return results[i].JobID < results[j].JobID })
	want := []Result{{JobID: 1, Value: 4}, {JobID: 2, Value: 9}, {JobID: 3, Value: 16}, {JobID: 4, Value: 25}, {JobID: 5, Value: 36}}
	for i := range want {
		if results[i] != want[i] {
			panic("unexpected worker result")
		}
	}
}
```

最小验证：把代码保存为 `worker-pool-concurrency-limit.go`，运行：

```bash
go run worker-pool-concurrency-limit.go
```

**坑**：只限制 goroutine 数量不够，还要考虑数据库连接池、API 限流和内存占用；如果 `results` 没有人持续消费，worker 仍可能被结果写入阻塞。

**检查**：worker 数是否来自下游容量，而不是拍脑袋的 CPU 核数；是否能证明最大并发不会超过 worker 数。
