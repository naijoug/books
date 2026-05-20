# 小接口由使用方定义

**问题**：什么时候应该抽接口？

**要点**：

- Go 接口是隐式实现，不需要在提供方提前声明大接口。
- 使用方只定义自己需要的方法。
- 小接口更容易测试和替换。

**示例**：

```go
type EmailSender interface {
	Send(ctx context.Context, to string, subject string, body string) error
}

func Notify(ctx context.Context, sender EmailSender, user User) error {
	return sender.Send(ctx, user.Email, "Welcome", "Hello")
}
```

**坑**：为了“架构感”提前定义 `UserServiceInterface` 这类大接口，最后会变成难维护的抽象层。

**检查**：接口是否只有当前包真正需要的方法？
