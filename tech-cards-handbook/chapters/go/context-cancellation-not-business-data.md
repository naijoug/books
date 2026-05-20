# `context.Context` 传递取消信号，不传业务参数

**问题**：请求超时、用户取消、服务关闭时，如何让下游任务一起停止？

**要点**：

- `context` 放在函数第一个参数。
- 用它传递取消、截止时间和请求级元信息。
- 不要把业务参数塞进 `context.Value`。

**示例**：

```go
func FetchUser(ctx context.Context, id string) (*User, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, "/users/"+id, nil)
	if err != nil {
		return nil, err
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return decodeUser(resp.Body)
}
```

**坑**：创建了 `context.WithTimeout` 却忘记 `defer cancel()`，会让 timer 资源停留更久。

**检查**：所有可能阻塞的 I/O 调用是否接收或派生自上游 `ctx`？
