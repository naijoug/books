# Swift 字符串插值比拼接更清晰

**问题**：如何把变量放进字符串？

**要点**：

- 使用 `\(value)` 做字符串插值。
- 多行文本用三引号。
- 插值比多个 `+` 更容易读，也更不容易漏空格。

**示例**：

```swift
import Foundation

func profileLine(name: String, age: Int) -> String {
    "Hello, \(name)! You are \(age) years old."
}

func receipt(items: [String], total: Double) -> String {
    let itemList = items.joined(separator: ", ")
    return """
    Items: \(itemList)
    Total: $\(String(format: "%.2f", total))
    """
}

assert(profileLine(name: "Ada", age: 30) == "Hello, Ada! You are 30 years old.")
assert(receipt(items: ["Book", "Pen"], total: 12.5) == """
Items: Book, Pen
Total: $12.50
""")
```

最小验证：把上面的代码保存为 `swift-string-interpolation.swift`，运行：

```bash
swift swift-string-interpolation.swift
```

**坑**：大量业务文案不要散落在代码里，真实应用应接入本地化和资源管理。金额、日期等格式化也不要只靠普通插值，应该使用 `FormatStyle` 或本地化资源统一处理。

**检查**：字符串是否需要本地化？插值里的值是否需要固定格式？需要就不要硬编码在组件内部。
