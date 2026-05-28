# Swift 可选绑定替代强制解包

**问题**：为什么 `optional!` 是常见崩溃来源？

**要点**：

- `String?` 表示可能有值，也可能是 `nil`。
- `if let` 安全解包。
- `??` 提供默认值。

**示例**：

```swift
func greeting(for optionalName: String?) -> String {
    if let name = optionalName {
        return "Hello, \(name)"
    } else {
        return "No name"
    }
}

func displayName(for optionalName: String?) -> String {
    optionalName ?? "Guest"
}

assert(greeting(for: "Ada") == "Hello, Ada")
assert(greeting(for: nil) == "No name")
assert(displayName(for: "Grace") == "Grace")
assert(displayName(for: nil) == "Guest")
```

最小验证：

```bash
swift swift-optional-binding-no-force-unwrap.swift
```

**坑**：强制解包只适合你能证明绝不为 nil 的场景，否则就是运行时崩溃。

**检查**：把上面的代码保存为 `swift-optional-binding-no-force-unwrap.swift` 并运行，命令应以退出码 `0` 结束；每个 `!` 是否都有明确不变量支撑？
