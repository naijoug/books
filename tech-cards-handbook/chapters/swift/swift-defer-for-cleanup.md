# Swift `defer` 把清理逻辑贴近资源获取

**问题**：函数里有多个 `return` 或 `throw` 分支时，如何保证临时状态、文件句柄、锁或 loading 状态一定被恢复？

**要点**：

- `defer` 中的代码会在当前作用域退出前执行。
- 把“获取资源”和“释放资源”放在相邻位置，减少遗漏。
- 多个 `defer` 按后进先出顺序执行，适合成对清理嵌套资源。

**示例**：

```swift
import Foundation

enum ParseError: Error {
    case emptyFile
}

func countNonEmptyLines(at url: URL) throws -> Int {
    let handle = try FileHandle(forReadingFrom: url)
    defer { try? handle.close() } // 无论后面 return 还是 throw，都会先关闭文件。

    let data = try handle.readToEnd() ?? Data()
    let text = String(decoding: data, as: UTF8.self)
    let lines = text.split(separator: "\n").filter { !$0.isEmpty }

    guard !lines.isEmpty else {
        throw ParseError.emptyFile
    }

    return lines.count
}
```

```swift
let tempURL = FileManager.default.temporaryDirectory
    .appendingPathComponent("swift-defer-for-cleanup.txt")

try "first\n\nsecond\n".write(to: tempURL, atomically: true, encoding: .utf8)
defer { try? FileManager.default.removeItem(at: tempURL) }

let lineCount = try countNonEmptyLines(at: tempURL)
assert(lineCount == 2)
assert(!FileManager.default.fileExists(atPath: tempURL.path) == false) // 退出作用域前文件仍存在。

try "\n".write(to: tempURL, atomically: true, encoding: .utf8)
do {
    _ = try countNonEmptyLines(at: tempURL)
    assertionFailure("empty file should throw")
} catch ParseError.emptyFile {
    assert(FileManager.default.fileExists(atPath: tempURL.path))
}
```

**最小验证**：把两个代码块保存为 `swift-defer-for-cleanup.swift`，执行：

```bash
swift swift-defer-for-cleanup.swift
```

命令应以退出码 `0` 结束，且没有断言失败。

**坑**：`defer` 不是异步取消机制，也不应该承载主要业务流程；如果清理本身可能失败，要明确记录或设计补偿，而不是用 `try?` 悄悄吞掉关键错误。

**检查**：看到 `isLoading = true`、`lock.lock()`、打开文件、开始事务这类获取动作时，能否在相邻几行找到对应的 `defer` 清理？示例是否能用 `swift <file>.swift` 独立跑通，并覆盖提前 `throw` 或多个退出路径？
