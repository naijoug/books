# `sync.WaitGroup` 等待一组 goroutine 完成

**问题**：启动多个 goroutine 后，主流程如何知道它们都结束了？

**要点**：

- 启动 goroutine 前调用 `Add(1)`。
- goroutine 结束时 `defer Done()`。
- 主流程用 `Wait()` 阻塞到计数归零。

**示例**：

```go
package main

import (
	"sort"
	"sync"
)

func worker(id int, wg *sync.WaitGroup, done chan<- int) {
	defer wg.Done()
	done <- id
}

func runWorkers(count int) []int {
	var wg sync.WaitGroup
	done := make(chan int, count)

	for i := 0; i < count; i++ {
		wg.Add(1)
		go worker(i, &wg, done)
	}

	wg.Wait()
	close(done)

	ids := make([]int, 0, count)
	for id := range done {
		ids = append(ids, id)
	}
	sort.Ints(ids)
	return ids
}

func main() {
got := runWorkers(5)
want := []int{0, 1, 2, 3, 4}
if len(got) != len(want) {
	panic("worker count mismatch")
}
for i := range want {
	if got[i] != want[i] {
		panic("worker id mismatch")
	}
}
}
```

最小验证：

```bash
go run sync-waitgroup-goroutine-completion.go
```

如果只看核心结构，可以把上面的 `runWorkers` 简化成：启动前 `wg.Add(1)`，goroutine 入口 `defer wg.Done()`，主流程最后 `wg.Wait()`。

**坑**：`Add` 放到 goroutine 内部可能和 `Wait` 竞争，导致主流程提前结束。

**检查**：`Add` 是否在启动 goroutine 之前发生？`Done` 是否用 `defer` 保证执行？
