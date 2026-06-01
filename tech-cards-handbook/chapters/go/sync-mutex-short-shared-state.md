# `sync.Mutex` 保护短小共享状态

**问题**：Go 提倡 channel，是否就不该用锁？

**要点**：

- channel 适合传递所有权或事件；mutex 适合保护一小块共享状态，比如计数器、缓存索引、连接状态。
- 锁的临界区要短：只包住读写共享字段的几行代码，避免持锁做慢 I/O、网络请求或复杂计算。
- 暴露方法时用指针接收者，避免复制含有 mutex 的结构体；必要时在结构体里嵌入不可复制约束或在代码审查中明确禁止复制。

**示例**：

```go
package main

import (
	"fmt"
	"sync"
)

type SafeCounter struct {
	mu    sync.Mutex
	value int
}

func (c *SafeCounter) Inc() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.value++
}

func (c *SafeCounter) Value() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.value
}

func main() {
	const goroutines = 8
	const incrementsPerGoroutine = 1000

	counter := &SafeCounter{}
	var wg sync.WaitGroup

	for worker := 0; worker < goroutines; worker++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < incrementsPerGoroutine; i++ {
				counter.Inc()
			}
		}()
	}

	wg.Wait()

	want := goroutines * incrementsPerGoroutine
	if got := counter.Value(); got != want {
		panic(fmt.Sprintf("counter=%d, want %d", got, want))
	}
}
```

**坑**：

- 复制含有 mutex 的结构体会制造多个锁保护同一份语义数据，容易出错；通常通过指针传递。
- `defer Unlock` 简洁且不容易漏解锁；在极热路径里可以手写 `Unlock`，但要更谨慎处理提前返回和 panic。
- 不要在持锁期间调用未知回调或可能阻塞的外部 API，否则调用方很容易把锁等待放大成死锁或长尾延迟。

**检查**：被锁保护的字段是否只在持锁期间读写？临界区里是否只做短小、可预测的内存操作？
