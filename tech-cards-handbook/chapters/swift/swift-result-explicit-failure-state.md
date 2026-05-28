# Swift `Result` 把成功和失败放进同一个值

**问题**：当一个异步回调、缓存读取或批量任务可能失败时，如何避免用多个可选值或布尔值表达状态？

**要点**：

- `Result<Success, Failure>` 明确表达“要么有成功值，要么有失败原因”。
- `Failure` 必须遵守 `Error`，适合用领域错误枚举描述可预期失败。
- 用 `switch` 同时处理 `.success` 和 `.failure`，不要只取成功值忽略错误。
- `async throws` 更适合线性异步流程；`Result` 更适合把结果保存、传递、合并或放进回调参数。

**示例**：

```swift
enum ProfileError: Error {
    case missingToken
    case invalidResponse
}

struct Profile {
    let name: String
}

func readCachedProfile(token: String?) -> Result<Profile, ProfileError> {
    guard token != nil else {
        return .failure(.missingToken)
    }

    let cachedName = "Ada"
    guard !cachedName.isEmpty else {
        return .failure(.invalidResponse)
    }

    return .success(Profile(name: cachedName))
}

var title = ""
let currentToken: String? = nil
let result = readCachedProfile(token: currentToken)

switch result {
case .success(let profile):
    title = "Hello, \(profile.name)"
case .failure(.missingToken):
    title = "Please sign in"
case .failure(.invalidResponse):
    title = "Cached profile is broken"
}

assert(title == "Please sign in")
```

把多个结果收集起来时，`Result` 也比“值数组 + 错误数组”更不容易错位：

```swift
let tokens: [String?] = ["token", nil]
let results: [Result<Profile, ProfileError>] = tokens.map(readCachedProfile)
let loaded = results.compactMap { try? $0.get() }

assert(loaded.map(\.name) == ["Ada"])
assert(results.contains { item in
    if case .failure(.missingToken) = item {
        return true
    }
    return false
})
```

**坑**：

- 不要把所有失败都塞进 `String`；调用方无法稳定分支，只能匹配文本。
- 不要用 `(Profile?, Error?)` 表达结果；它可能出现“两者都有”或“两者都没有”的非法状态。
- 不要在所有函数里机械套 `Result`。如果调用方马上 `try`，`throws` 往往更自然。

**检查**：这个接口的调用方是否能从类型签名看出失败原因集合？每个 `Result` 是否都有 `.success` 和 `.failure` 的处理路径？把两个示例保存为同一个 `swift-result-explicit-failure-state.swift` 后，运行：

```bash
swift swift-result-explicit-failure-state.swift
```

如果命令无输出且退出码为 0，说明示例覆盖了缺 token、成功读取和批量收集三条路径。
