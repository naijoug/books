# `Option` 表达“可能没有”

**问题**：如何避免空指针式错误？

**要点**：

- `Option<T>` 只有 `Some(T)` 和 `None`，把“可能没有”放进类型系统。
- 用 `match`、`if let`、`map`、`unwrap_or` 处理，而不是假装值一定存在。
- 不要在业务代码里随手 `unwrap()`；让调用方能看到并处理缺失分支。

**示例**：

```rust
fn first_char(input: &str) -> Option<char> {
    input.chars().next()
}

fn display_label(input: &str) -> char {
    first_char(input).unwrap_or('?')
}

fn describe_first_char(input: &str) -> String {
    match first_char(input) {
        Some(ch) => format!("first char is {ch}"),
        None => "input is empty".to_string(),
    }
}

fn main() {
    assert_eq!(first_char("rust"), Some('r'));
    assert_eq!(first_char(""), None);

    assert_eq!(display_label("agent"), 'a');
    assert_eq!(display_label(""), '?');

    assert_eq!(describe_first_char("tool"), "first char is t");
    assert_eq!(describe_first_char(""), "input is empty");

    if let Some(ch) = first_char("verify") {
        println!("verified first char: {ch}");
    }

    let upper = first_char("rust").map(|ch| ch.to_ascii_uppercase());
    assert_eq!(upper, Some('R'));

    println!("option demo done");
}
```

**坑**：`unwrap()` 适合测试、原型或绝不可能失败的内部不变量，不适合外部输入。对外部输入使用 `match` 或默认值，可以让失败路径留在代码审查视野里。

**检查**：看到 `unwrap()` 时，确认 panic 是否是可接受的失败方式；如果不是，就把返回类型保留为 `Option<T>` 或转成带上下文的 `Result<T, E>`。
