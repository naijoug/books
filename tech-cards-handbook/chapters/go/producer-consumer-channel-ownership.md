# 生产者-消费者用 channel 传递所有权

**问题**：一个 goroutine 生产数据，多个 goroutine 消费数据，如何组织？

**要点**：

- 生产者向 channel 发送数据，并在发送完毕后关闭 channel。
- 消费者用 `for item := range ch` 读取，直到 channel 关闭。
- channel 里传递的是“下一步处理权”：谁从 channel 收到值，谁负责完成这份工作。
- 用方向类型 `chan<- T` / `<-chan T` 把发送方、接收方的职责写进函数签名。

**示例**：

```go
package main

import "sync"

type job struct {
	ID    int
	Value int
}

type result struct {
	Consumer string
	JobID    int
	Value    int
}

func producer(out chan<- job, count int) {
	defer close(out)
	for i := 1; i <= count; i++ {
		out <- job{ID: i, Value: i * 10}
	}
}

func consumer(name string, in <-chan job, out chan<- result, wg *sync.WaitGroup) {
	defer wg.Done()
	for item := range in {
		out <- result{
			Consumer: name,
			JobID:    item.ID,
			Value:    item.Value * 2,
		}
	}
}

func main() {
	jobs := make(chan job)
	results := make(chan result)

	go producer(jobs, 5)

	var wg sync.WaitGroup
	for _, name := range []string{"consumer-A", "consumer-B"} {
		wg.Add(1)
		go consumer(name, jobs, results, &wg)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	seen := map[int]bool{}
	for res := range results {
		if res.Consumer == "" {
			panic("result should record which consumer handled the job")
		}
		if seen[res.JobID] {
			panic("a job should be consumed by exactly one consumer")
		}
		seen[res.JobID] = true
		if res.Value != res.JobID*20 {
			panic("consumer should transform the job value")
		}
	}

	if len(seen) != 5 {
		panic("all produced jobs should be consumed before results closes")
	}
}
```

最小验证：

```bash
go run producer-consumer-channel-ownership.go
```

**坑**：消费者不负责关闭输入 channel；多个生产者关闭同一个 channel 需要额外协调。输出 channel 通常也由“知道所有消费者何时退出”的协调者关闭，而不是由任意一个消费者关闭。

**检查**：channel 的方向类型是否表达清楚了发送方和接收方？每个 `close` 是否都由唯一拥有者或协调者执行？
