# `select` 用来同时等待结果、超时和取消

**问题**：如何同时等待任务结果和超时？

**要点**：

- `select` 在多个 channel 操作中选择一个可执行分支。
- 常见组合是结果 channel、`time.After`、`ctx.Done()`。
- 超时更推荐用 `context.WithTimeout` 贯穿调用链。

**示例**：

```go
func longRunningTask() <-chan string {
	ch := make(chan string, 1)
	go func() {
		time.Sleep(2 * time.Second)
		ch <- "done"
	}()
	return ch
}

select {
case result := <-longRunningTask():
	fmt.Println(result)
case <-time.After(time.Second):
	fmt.Println("timeout")
}
```

**坑**：`time.After` 在循环里反复创建 timer 可能带来额外分配；复杂循环用 `time.NewTimer` 并复用/停止。

**检查**：等待外部结果时，是否有取消或超时路径？
