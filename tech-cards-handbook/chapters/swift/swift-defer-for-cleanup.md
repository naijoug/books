# Swift `defer` 把清理逻辑贴近资源获取

**问题**：函数里有多个 `return` 或 `throw` 分支时，如何保证临时状态、文件句柄、锁或 loading 状态一定被恢复？

**要点**：

- `defer` 中的代码会在当前作用域退出前执行。
- 把“获取资源”和“释放资源”放在相邻位置，减少遗漏。
- 多个 `defer` 按后进先出顺序执行，适合成对清理嵌套资源。

**示例**：

```swift
final class ProfileViewModel: ObservableObject {
    @Published private(set) var isLoading = false
    @Published private(set) var profile: Profile?

    func reload(id: String) async {
        isLoading = true
        defer { isLoading = false }

        do {
            profile = try await api.fetchProfile(id: id)
        } catch {
            // 记录错误或更新错误状态；无论成功失败，isLoading 都会恢复。
            print("load profile failed: \(error)")
        }
    }
}
```

```swift
func countLines(at url: URL) throws -> Int {
    let handle = try FileHandle(forReadingFrom: url)
    defer { try? handle.close() }

    let data = try handle.readToEnd() ?? Data()
    return String(decoding: data, as: UTF8.self)
        .split(separator: "\n")
        .count
}
```

**坑**：`defer` 不是异步取消机制，也不应该承载主要业务流程；如果清理本身可能失败，要明确记录或设计补偿，而不是用 `try?` 悄悄吞掉关键错误。

**检查**：看到 `isLoading = true`、`lock.lock()`、打开文件、开始事务这类获取动作时，能否在相邻几行找到对应的 `defer` 清理？
