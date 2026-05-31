# `select` 用来同时等待结果、超时和取消

**问题**：调用外部服务、排队任务或后台 goroutine 时，如何同时等待“成功结果”“超时”和“上游取消”？

**要点**：

- `select` 在多个 channel 操作中选择一个已经就绪的分支；它适合把结果、超时、取消放进同一个等待点。
- 对外暴露的函数优先接收 `context.Context`，用 `ctx.Done()` 作为取消路径；超时通常用 `context.WithTimeout` 由调用方统一控制。
- 结果 channel 建议带缓冲或确保有接收方，否则超时/取消返回后，后台 goroutine 可能因为发送结果而泄漏。
- 如果只在单次等待中兜底超时，`time.After` 简洁；如果在循环里反复等待，用 `time.NewTimer` 并正确 `Stop`/排空更可控。

**示例**：

```go
package main

import (
	"context"
	"errors"
	"fmt"
	"time"
)

type taskResult struct {
	value string
	err   error
}

func longRunningTask(ctx context.Context, delay time.Duration) <-chan taskResult {
	results := make(chan taskResult, 1)

	go func() {
		select {
		case <-time.After(delay):
			results <- taskResult{value: "done"}
		case <-ctx.Done():
			results <- taskResult{err: ctx.Err()}
		}
	}()

	return results
}

func waitForTask(parent context.Context, delay, timeout time.Duration) (string, error) {
	ctx, cancel := context.WithTimeout(parent, timeout)
	defer cancel()

	select {
	case result := <-longRunningTask(ctx, delay):
		if result.err != nil {
			return "", result.err
		}
		return result.value, nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}

func main() {
	value, err := waitForTask(context.Background(), 10*time.Millisecond, 100*time.Millisecond)
	if err != nil || value != "done" {
		panic(fmt.Sprintf("want success, got value=%q err=%v", value, err))
	}

	value, err = waitForTask(context.Background(), 100*time.Millisecond, 10*time.Millisecond)
	if !errors.Is(err, context.DeadlineExceeded) || value != "" {
		panic(fmt.Sprintf("want deadline exceeded, got value=%q err=%v", value, err))
	}

	parent, cancel := context.WithCancel(context.Background())
	cancel()
	value, err = waitForTask(parent, 10*time.Millisecond, 100*time.Millisecond)
	if !errors.Is(err, context.Canceled) || value != "" {
		panic(fmt.Sprintf("want canceled, got value=%q err=%v", value, err))
	}
}
```

**坑**：

- `select` 只能等待 channel 操作；普通函数调用必须先放到 goroutine 或可取消的 API 里。
- 超时或取消后如果后台 goroutine 仍要发送结果，结果 channel 没有缓冲会卡住；上例使用容量为 1 的 channel，让 goroutine 能完成发送并退出。
- `time.After` 在循环里反复创建 timer 可能带来额外分配；复杂循环用 `time.NewTimer`，并在提前退出时 `Stop` 和排空。

**检查**：等待外部结果时，是否有明确的取消或超时路径？超时/取消返回后，负责产生结果的 goroutine 是否也能退出？
