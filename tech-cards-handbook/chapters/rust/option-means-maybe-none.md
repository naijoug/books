# `Option` 表达“可能没有”

**问题**：如何避免空指针式错误？

**要点**：

- `Option<T>` 只有 `Some(T)` 和 `None`。
- 用 `match`、`if let`、`map`、`unwrap_or` 处理。
- 不要在业务代码里随手 `unwrap()`。

**示例**：

```rust
fn first_char(input: &str) -> Option<char> {
    input.chars().next()
}

let label = first_char("rust").unwrap_or('?');
```

**坑**：`unwrap()` 适合测试、原型或绝不可能失败的内部不变量，不适合外部输入。

**检查**：看到 `unwrap()` 时，确认 panic 是否是可接受的失败方式。
