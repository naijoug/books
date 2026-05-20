# Swift 可选绑定替代强制解包

**问题**：为什么 `optional!` 是常见崩溃来源？

**要点**：

- `String?` 表示可能有值，也可能是 `nil`。
- `if let` 安全解包。
- `??` 提供默认值。

**示例**：

```swift
var optionalName: String? = "Ada"

if let name = optionalName {
    print("Hello, \(name)")
} else {
    print("No name")
}

let displayName = optionalName ?? "Guest"
```

**坑**：强制解包只适合你能证明绝不为 nil 的场景，否则就是运行时崩溃。

**检查**：每个 `!` 是否都有明确不变量支撑？
