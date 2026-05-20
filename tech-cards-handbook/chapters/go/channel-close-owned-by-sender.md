# channel 的关闭权属于发送方

**问题**：什么时候该关闭 channel？

**要点**：

- 发送方关闭 channel，用于表示“不再发送”。
- 接收方通过 `for range` 消费直到关闭。
- 多发送方场景不要随便关闭共享 channel，通常需要额外协调。

**示例**：

```go
func produce(out chan<- int) {
	defer close(out)
	for i := 0; i < 3; i++ {
		out <- i
	}
}

func main() {
	ch := make(chan int)
	go produce(ch)
	for n := range ch {
		fmt.Println(n)
	}
}
```

**坑**：向已关闭 channel 发送会 panic；重复关闭也会 panic。

**检查**：代码里每个 `close(ch)` 是否都能回答“这个 goroutine 是唯一发送方或关闭协调者”？
