# `sync.Mutex` 保护短小共享状态

**问题**：Go 提倡 channel，是否就不该用锁？

**要点**：

- channel 适合传递所有权或事件。
- mutex 适合保护短小的共享状态。
- 锁住后尽快释放，避免持锁做慢 I/O。

**示例**：

```go
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
```

**坑**：复制含有 mutex 的结构体会制造多个锁保护同一份语义数据，容易出错。通常通过指针传递。

**检查**：被锁保护的字段是否只在持锁期间读写？
