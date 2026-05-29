# Swift async/await 让异步流程保持顺序可读

**问题**：如何避免回调层层嵌套？

**要点**：

- 异步函数用 `async` 标注，调用处用 `await` 明确等待点。
- 可能失败的异步函数用 `async throws`，用普通 `do/catch` 串起成功和失败路径。
- UI 更新回到主线程或主 actor；业务层先把异步流程写成可测试的小函数。

**示例**：

```swift
import Foundation

struct User: Equatable {
    let id: String
    let name: String
}

enum LoadUserError: Error, Equatable {
    case notFound
}

func loadUser(id: String) async throws -> User {
    try await Task.sleep(nanoseconds: 1_000_000)

    if id == "missing" {
        throw LoadUserError.notFound
    }

    return User(id: id, name: "Hermes")
}

func greeting(for id: String) async -> String {
    do {
        let user = try await loadUser(id: id)
        return "Hello, \(user.name)!"
    } catch LoadUserError.notFound {
        return "User not found"
    } catch {
        return "Failed to load user"
    }
}

let loaded = try await loadUser(id: "42")
let successMessage = await greeting(for: "42")
let missingMessage = await greeting(for: "missing")

assert(loaded == User(id: "42", name: "Hermes"))
assert(successMessage == "Hello, Hermes!")
assert(missingMessage == "User not found")
```

最小验证：保存为 `swift-async-await-readable-flow.swift` 后运行：

```bash
swift swift-async-await-readable-flow.swift
```

**坑**：异步不等于后台线程。涉及 UI 状态时要确认执行上下文；涉及取消时，不要吞掉 `CancellationError`，也不要把 loading 状态只放在成功路径里关闭。

**检查**：取消、失败、loading 三种状态是否都被 UI 表达出来？示例脚本能否同时跑通成功路径和失败路径的断言？
