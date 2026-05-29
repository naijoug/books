# Swift 数组和字典都要处理“可能没有”

**问题**：访问集合元素时，哪里最容易崩？

**要点**：

- 数组下标越界会崩。
- 字典读取返回 optional。
- 遍历带索引用 `enumerated()`。

**示例**：

```swift
func numberedItems(_ items: [String]) -> [String] {
    items.enumerated().map { index, item in
        "\(index): \(item)"
    }
}

func item(at index: Int, in items: [String]) -> String? {
    guard items.indices.contains(index) else { return nil }
    return items[index]
}

func capital(of country: String, in capitals: [String: String]) -> String {
    capitals[country] ?? "Unknown"
}

let fruits = ["Apple", "Banana", "Orange"]
assert(numberedItems(fruits) == ["0: Apple", "1: Banana", "2: Orange"])
assert(item(at: 1, in: fruits) == "Banana")
assert(item(at: 3, in: fruits) == nil)

let capitals = ["China": "Beijing", "Japan": "Tokyo"]
assert(capital(of: "China", in: capitals) == "Beijing")
assert(capital(of: "France", in: capitals) == "Unknown")
```

最小验证：保存为 `swift-array-dictionary-missing-values.swift` 后运行：

```bash
swift swift-array-dictionary-missing-values.swift
```

**坑**：不要假设外部数据一定包含某个 key；数组也不要先用 `count` 心算下标，优先把越界访问包成返回 optional 的小函数。

**检查**：所有数组下标和字典读取是否都处理了不存在的情况？是否有 `assert` 覆盖命中和缺失两条路径？
