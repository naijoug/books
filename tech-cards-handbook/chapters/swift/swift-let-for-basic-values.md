# Swift 基础值优先用 `let`

**问题**：什么时候用 `let`，什么时候用 `var`？

**要点**：

- `let` 声明常量，赋值后不能改。
- `var` 声明变量，可以重新赋值。
- 默认用 `let`，只有确实需要变化时用 `var`。

**示例**：

```swift
struct Player {
    let name: String
    let level: Int
}

var score = 100
score = 99

let player = Player(name: "Ada", level: 30)

assert(player.name == "Ada")
assert(player.level == 30)
assert(score == 99)
```

最小验证：把示例保存为 `swift-let-for-basic-values.swift`，运行 `swift swift-let-for-basic-values.swift`，应无输出、无断言失败。

**坑**：过度使用 `var` 会让状态变化边界不清楚，调试时更难判断谁改了值。若取消注释 `player.level = 31`，编译器会直接报错，因为 `let` 属性不能重新赋值。

**检查**：这个值声明后是否真的会变？不会就用 `let`。
