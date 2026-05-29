# Swift `switch` 适合表达离散分支

**问题**：多个互斥分支用 `if/else` 还是 `switch`？

**要点**：

- 离散枚举、状态、等级适合 `switch`。
- `switch` 可以让分支结构更清晰。
- 对 `enum` 使用 `switch` 时，编译器能提示遗漏分支。

**示例**：

```swift
enum Grade {
    case excellent
    case good
    case okay
    case needsWork
}

func message(for grade: Grade) -> String {
    switch grade {
    case .excellent:
        return "Excellent"
    case .good:
        return "Good"
    case .okay:
        return "Okay"
    case .needsWork:
        return "Needs work"
    }
}

assert(message(for: .excellent) == "Excellent")
assert(message(for: .good) == "Good")
assert(message(for: .okay) == "Okay")
assert(message(for: .needsWork) == "Needs work")
```

最小验证：把示例保存为 `swift-switch-discrete-branches.swift`，运行：

```bash
swift swift-switch-discrete-branches.swift
```

**坑**：如果条件是范围和复杂布尔表达式，`if/else` 可能更直接；如果离散状态本来就能建模成 `enum`，不要用裸字符串让遗漏分支只能在运行时暴露。

**检查**：这些分支是否来自同一个离散状态集合？如果是，能否先建模成 `enum`，再让 `switch` 穷尽覆盖？
