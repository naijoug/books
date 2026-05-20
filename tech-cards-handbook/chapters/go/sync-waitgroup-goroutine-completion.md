# `sync.WaitGroup` 等待一组 goroutine 完成

**问题**：启动多个 goroutine 后，主流程如何知道它们都结束了？

**要点**：

- 启动 goroutine 前调用 `Add(1)`。
- goroutine 结束时 `defer Done()`。
- 主流程用 `Wait()` 阻塞到计数归零。

**示例**：

```go
func worker(id int, wg *sync.WaitGroup) {
	defer wg.Done()
	fmt.Printf("worker %d start\n", id)
	time.Sleep(time.Second)
	fmt.Printf("worker %d done\n", id)
}

func main() {
	var wg sync.WaitGroup
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go worker(i, &wg)
	}
	wg.Wait()
}
```

**坑**：`Add` 放到 goroutine 内部可能和 `Wait` 竞争，导致主流程提前结束。

**检查**：`Add` 是否在启动 goroutine 之前发生？`Done` 是否用 `defer` 保证执行？
