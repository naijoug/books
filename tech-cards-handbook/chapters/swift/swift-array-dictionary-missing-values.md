# Swift 数组和字典都要处理“可能没有”

**问题**：访问集合元素时，哪里最容易崩？

**要点**：

- 数组下标越界会崩。
- 字典读取返回 optional。
- 遍历带索引用 `enumerated()`。

**示例**：

```swift
let fruits = ["Apple", "Banana", "Orange"]

for (index, fruit) in fruits.enumerated() {
    print("\(index): \(fruit)")
}

let capitals = ["China": "Beijing", "Japan": "Tokyo"]
let capital = capitals["China"] ?? "Unknown"
```

**坑**：不要假设外部数据一定包含某个 key。

**检查**：所有下标和字典读取是否都处理了不存在的情况？
