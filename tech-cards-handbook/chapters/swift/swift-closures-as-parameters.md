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

func keepPassingScores(_ scores: [Int], minimum: Int) -> [Int] {
    scores.filter { score in
        score >= minimum
    }
}

let doubled = apply(numbers: [1, 2, 3]) { $0 * 2 }
assert(doubled == [2, 4, 6])

let bonus = 5
let withBonus = apply(numbers: [10, 20]) { score in
    score + bonus
}
assert(withBonus == [15, 25])
assert(keepPassingScores([58, 60, 91], minimum: 60) == [60, 91])
```

最小验证：把示例保存为 `swift-closures-as-parameters.swift`，运行 `swift swift-closures-as-parameters.swift`，应无输出且退出码为 0。

**坑**：闭包捕获 class 实例时可能形成循环引用，需要根据场景使用 `weak`；闭包若会被长期保存，也要确认捕获的外部变量是否会被意外延长生命周期。

**检查**：闭包是否会被长期持有？如果会，检查引用循环；如果闭包依赖外部状态，是否有测试覆盖捕获值变化后的结果。
