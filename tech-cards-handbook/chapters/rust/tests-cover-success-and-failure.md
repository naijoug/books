# 测试要覆盖成功路径和失败路径

**问题**：Rust 代码如何把错误处理也测出来？

**要点**：

- 单元测试写在同文件 `#[cfg(test)]` 模块里。
- `assert_eq!` 验证结果，`matches!` 验证枚举分支。
- 失败路径和边界输入要和成功路径一样重视。

**示例**：

```rust
fn parse_port(input: &str) -> Result<u16, String> {
    input.parse::<u16>().map_err(|_| "invalid port".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_valid_port() {
        assert_eq!(parse_port("8080"), Ok(8080));
    }

    #[test]
    fn rejects_invalid_port() {
        assert!(matches!(parse_port("abc"), Err(_)));
    }
}
```

**坑**：只测试 happy path，会让错误类型、边界值和 panic 在上线后才暴露。

**检查**：每个返回 `Result` 的核心函数，是否至少有一个成功用例和一个失败用例？
