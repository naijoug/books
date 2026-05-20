# 生产者-消费者用 channel 传递所有权

**问题**：一个 goroutine 生产数据，多个 goroutine 消费数据，如何组织？

**要点**：

- 生产者向 channel 发送数据。
- 消费者用 `for item := range ch` 读取。
- 生产者发送完毕后关闭 channel。

**示例**：

```go
func producer(ch chan<- int, count int) {
	defer close(ch)
	for i := 0; i < count; i++ {
		ch <- i
	}
}

func consumer(ch <-chan int, name string) {
	for num := range ch {
		fmt.Println(name, num)
	}
}
```

**坑**：消费者不负责关闭 channel；多个生产者关闭同一个 channel 需要额外协调。

**检查**：channel 的方向类型是否表达清楚了发送方和接收方？
