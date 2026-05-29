# `context.Context` 传递取消信号，不传业务参数

**问题**：请求超时、用户取消、服务关闭时，如何让下游任务一起停止？

**要点**：

- `context` 放在函数第一个参数。
- 用它传递取消、截止时间和请求级元信息。
- 不要把业务参数塞进 `context.Value`。

**示例**：

```go
package main

import (
	"context"
	"errors"
	"fmt"
	"time"
)

type User struct {
	ID   string
	Name string
}

var errUserNotFound = errors.New("user not found")

func FetchUser(ctx context.Context, id string) (*User, error) {
	if id == "" {
		return nil, fmt.Errorf("id is required")
	}

	select {
	case <-time.After(20 * time.Millisecond):
		if id == "42" {
			return &User{ID: "42", Name: "Ada"}, nil
		}
		return nil, fmt.Errorf("fetch user %q: %w", id, errUserNotFound)
	case <-ctx.Done():
		return nil, fmt.Errorf("fetch user %q: %w", id, ctx.Err())
	}
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()

	user, err := FetchUser(ctx, "42")
	if err != nil {
		panic(err)
	}
	if user.Name != "Ada" {
		panic(fmt.Sprintf("unexpected user: %#v", user))
	}

	cancelled, stop := context.WithCancel(context.Background())
	stop()
	_, err = FetchUser(cancelled, "42")
	if !errors.Is(err, context.Canceled) {
		panic(fmt.Sprintf("want context.Canceled, got %v", err))
	}
}
```

最小验证：保存为 `context-cancellation-not-business-data.go`，运行 `go run context-cancellation-not-business-data.go`，程序应静默退出。

**坑**：创建了 `context.WithTimeout` 却忘记 `defer cancel()`，会让 timer 资源停留更久；把 `id` 这类业务参数塞进 `context.Value`，会让函数签名变得不透明，也绕过了编译器检查。

**检查**：所有可能阻塞的 I/O 调用是否接收或派生自上游 `ctx`？业务参数是否仍然通过显式参数传入，而不是藏进 `ctx`？
