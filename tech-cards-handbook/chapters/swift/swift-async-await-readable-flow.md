# Swift async/await 让异步流程保持顺序可读

**问题**：如何避免回调层层嵌套？

**要点**：

- 异步函数用 `async` 标注。
- 可能失败的异步函数用 `async throws`。
- UI 更新回到主线程或主 actor。

**示例**：

```swift
func loadUser(id: String) async throws -> User {
    let url = URL(string: "https://example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}
```

**坑**：异步不等于后台线程。涉及 UI 状态时要确认执行上下文。

**检查**：取消、失败、loading 三种状态是否都被 UI 表达出来？
