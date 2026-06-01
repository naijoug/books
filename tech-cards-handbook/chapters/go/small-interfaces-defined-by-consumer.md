# 小接口由使用方定义

**问题**：什么时候应该抽接口？

**要点**：

- Go 接口是隐式实现，不需要在提供方提前声明大接口。
- 使用方只定义自己需要的方法：调用方需要 `Send`，就只在调用方附近声明 `Send`。
- 小接口更容易测试和替换，也更不容易被“为了架构感”的大抽象绑住。

**示例**：

```go
package main

import (
	"context"
	"errors"
	"fmt"
	"strings"
)

type User struct {
	Email string
}

// EmailSender 由 Notify 的使用方定义，只暴露当前函数真正需要的 Send。
type EmailSender interface {
	Send(ctx context.Context, to string, subject string, body string) error
}

func Notify(ctx context.Context, sender EmailSender, user User) error {
	if user.Email == "" {
		return errors.New("missing user email")
	}
	return sender.Send(ctx, user.Email, "Welcome", "Hello")
}

// fakeSender 不需要声明“实现了 EmailSender”；只要方法集合匹配，就能作为测试替身传入。
type fakeSender struct {
	calls []string
	err   error
}

func (f *fakeSender) Send(ctx context.Context, to string, subject string, body string) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	default:
	}

	f.calls = append(f.calls, fmt.Sprintf("%s|%s|%s", to, subject, body))
	return f.err
}

func main() {
	ctx := context.Background()
	fake := &fakeSender{}

	if err := Notify(ctx, fake, User{Email: "ada@example.com"}); err != nil {
		panic(err)
	}
	if got, want := len(fake.calls), 1; got != want {
		panic(fmt.Sprintf("calls=%d want=%d", got, want))
	}
	if !strings.Contains(fake.calls[0], "ada@example.com|Welcome|Hello") {
		panic("unexpected send payload: " + fake.calls[0])
	}

	if err := Notify(ctx, fake, User{}); err == nil || !strings.Contains(err.Error(), "missing user email") {
		panic("expected missing email error")
	}
}
```

**坑**：为了“架构感”提前定义 `UserServiceInterface`、`RepositoryInterface` 这类大接口，最后会把提供方的全部能力都复制进抽象层；调用方被迫依赖自己并不需要的方法，测试替身也要实现一堆无关行为。

**检查**：接口是否只有当前包真正需要的方法？如果删除某个方法，当前调用方是否仍然能工作？如果能，就说明这个方法不该在这个接口里。
