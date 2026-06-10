# 重试策略要显式化，而不是藏在错误处理循环里

**问题**：调用数据库、HTTP API、队列或文件系统失败时，什么时候该重试？如果把 `for` 循环直接写在错误处理分支里，后续很容易看不清哪些错误可重试、最多试几次、退避多久，以及耗尽后返回什么。

**要点**：

- 先把错误分成可重试、不可重试和调用方需要处理的领域错误；不要靠字符串匹配底层错误消息。
- 用 `RetryPolicy` 之类的小结构体表达最大尝试次数和退避间隔，让策略能被测试、配置和复用。
- 重试函数只负责“按策略重新调用一次操作”；业务函数仍然负责把底层错误转换成领域错误。
- 重试耗尽后要返回最后一次失败，并用 `%w` 保留错误链；日志或上层 handler 才能看到根因。

| 维度 | 隐式循环 | 显式策略 |
|---|---|---|
| 可重试条件 | 散落在 `if err != nil` 里 | `isRetryable(err)` 单独定义 |
| 次数和退避 | 魔法数字写在循环体 | `RetryPolicy{MaxAttempts, Backoff}` |
| 测试方式 | 只能跑完整业务流程 | 可注入假操作和零退避 |
| 耗尽语义 | 经常只返回 `err` | 包装为 `retry exhausted: %w` |

**示例**：

```go
package main

import (
	"errors"
	"fmt"
	"time"
)

var (
	ErrTemporary = errors.New("temporary upstream error")
	ErrForbidden = errors.New("forbidden")
)

type RetryPolicy struct {
	MaxAttempts int
	Backoff     time.Duration
}

func (p RetryPolicy) validate() RetryPolicy {
	if p.MaxAttempts < 1 {
		p.MaxAttempts = 1
	}
	return p
}

func isRetryable(err error) bool {
	return errors.Is(err, ErrTemporary)
}

func withRetry(policy RetryPolicy, call func() error) error {
	policy = policy.validate()
	var last error

	for attempt := 1; attempt <= policy.MaxAttempts; attempt++ {
		err := call()
		if err == nil {
			return nil
		}
		if !isRetryable(err) {
			return fmt.Errorf("non-retryable failure: %w", err)
		}

		last = err
		if attempt < policy.MaxAttempts && policy.Backoff > 0 {
			time.Sleep(policy.Backoff)
		}
	}

	return fmt.Errorf("retry exhausted after %d attempts: %w", policy.MaxAttempts, last)
}

func main() {
	attempts := 0
	err := withRetry(RetryPolicy{MaxAttempts: 3}, func() error {
		attempts++
		if attempts < 3 {
			return fmt.Errorf("fetch profile attempt %d: %w", attempts, ErrTemporary)
		}
		return nil
	})
	if err != nil {
		panic(err)
	}
	fmt.Printf("success after %d attempts\n", attempts)

	blocked := withRetry(RetryPolicy{MaxAttempts: 3}, func() error {
		return fmt.Errorf("load invoice: %w", ErrForbidden)
	})
	if !errors.Is(blocked, ErrForbidden) {
		panic(fmt.Sprintf("expected forbidden error, got %v", blocked))
	}
	fmt.Println("non-retryable errors keep their root cause")
}
```

**坑**：

- 把 `time.Sleep`、最大次数和错误判断直接塞进 service 方法，导致每个调用点都有一份不同的重试规则。
- 用 `strings.Contains(err.Error(), "timeout")` 判断是否重试；底层 SDK 改了错误文案，恢复策略就失效。
- 重试耗尽后返回一个全新的错误字符串，忘记 `%w`，调用方无法用 `errors.Is` / `errors.As` 判断根因。
- 对不可重试错误也继续重试，放大权限错误、参数错误或幂等性问题。

**检查**：

- 可重试错误集合是否有稳定的哨兵错误、接口或领域错误类型，而不是散落的字符串判断？
- 最大尝试次数、退避间隔和是否开启重试是否能在测试里设成小值或零值？
- 重试耗尽后，`errors.Is` / `errors.As` 还能否命中最后一次失败的根因？
- handler 或 CLI 对外输出是否只暴露安全错误码，而不是直接拼接底层 SDK / 数据库错误？
