# Swift 闭包让行为可以作为参数传递

**问题**：如何把一段逻辑传给函数？

**要点**：

- 闭包可以捕获上下文。
- 常见于 `map`、回调、排序和异步完成处理。
- 简单闭包可用 `$0` 简写。

**示例**：

```swift
func apply(numbers: [Int], operation: (Int) -> Int) -> [Int] {
    numbers.map(operation)
}

let doubled = apply(numbers: [1, 2, 3]) { $0 * 2 }
```

**坑**：闭包捕获 class 实例时可能形成循环引用，需要根据场景使用 `weak`。

**检查**：闭包是否会被长期持有？如果会，检查引用循环。
