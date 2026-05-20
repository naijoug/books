# Swift `switch` 适合表达离散分支

**问题**：多个互斥分支用 `if/else` 还是 `switch`？

**要点**：

- 离散枚举、状态、等级适合 `switch`。
- `switch` 可以让分支结构更清晰。
- 对 enum 使用 switch 时，编译器能提示遗漏分支。

**示例**：

```swift
let grade = "B"

switch grade {
case "A":
    print("Excellent")
case "B":
    print("Good")
case "C":
    print("Okay")
default:
    print("Needs work")
}
```

**坑**：如果条件是范围和复杂布尔表达式，`if/else` 可能更直接。

**检查**：这些分支是否来自同一个离散状态集合？
