# Swift `struct` 适合值语义，`class` 适合共享身份

**问题**：Swift 里什么时候用 `struct`，什么时候用 `class`？

**要点**：

- `struct` 复制的是值，适合模型、配置、不可共享状态。
- `class` 复制的是引用，适合需要共享身份或继承的对象。
- SwiftUI 的数据模型通常优先从值语义开始。

**示例**：

```swift
struct Profile {
    var name: String
    var age: Int
}

var a = Profile(name: "Ada", age: 30)
var b = a
b.name = "Grace"

print(a.name) // Ada
print(b.name) // Grace
```

**坑**：把可变共享状态做成 `class` 后，多个地方修改同一对象，问题会更隐蔽。

**检查**：这个类型是否需要“同一个对象身份”？不需要时优先 `struct`。
