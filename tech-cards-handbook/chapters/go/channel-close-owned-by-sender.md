# channel 的关闭权属于发送方

**问题**：什么时候该关闭 channel？

**要点**：

- 发送方关闭 channel，用于表示“不再发送”。
- 接收方通过 `for range` 消费直到关闭。
- 多发送方场景不要随便关闭共享 channel，通常需要额外协调。

**示例**：

```go
package main

func produce(out chan<- int) {
	defer close(out)
	for i := 0; i < 3; i++ {
		out <- i
	}
}

func collect(in <-chan int) []int {
	values := make([]int, 0, 3)
	for n := range in {
		values = append(values, n)
	}
	return values
}

func main() {
	ch := make(chan int)
	go produce(ch)

	values := collect(ch)
	if len(values) != 3 || values[0] != 0 || values[1] != 1 || values[2] != 2 {
		panic("consumer should receive all produced values before channel closes")
	}

	_, ok := <-ch
	if ok {
		panic("channel should be closed after producer finishes")
	}
}
```

最小验证：

```bash
go run channel-close-owned-by-sender.go
```

**坑**：向已关闭 channel 发送会 panic；重复关闭也会 panic。多发送方要先用 `sync.WaitGroup` 等协调所有发送者结束，再由唯一协调者关闭。

**检查**：代码里每个 `close(ch)` 是否都能回答“这个 goroutine 是唯一发送方或关闭协调者”？
