# 测试要覆盖成功路径和失败路径

**问题**：Rust 代码如何把错误处理也测出来？

**要点**：

- 单元测试写在同文件 `#[cfg(test)]` 模块里。
- `assert_eq!` 验证结果，`matches!` 验证枚举分支。
- 失败路径和边界输入要和成功路径一样重视。

**示例**：

```rust
#[derive(Debug, PartialEq, Eq)]
enum PortError {
    Empty,
    NotNumber,
    Reserved(u16),
}

fn parse_service_port(input: &str) -> Result<u16, PortError> {
    let trimmed = input.trim();

    if trimmed.is_empty() {
        return Err(PortError::Empty);
    }

    let port = trimmed
        .parse::<u16>()
        .map_err(|_| PortError::NotNumber)?;

    if port < 1024 {
        return Err(PortError::Reserved(port));
    }

    Ok(port)
}

fn build_endpoint(host: &str, port: &str) -> Result<String, PortError> {
    let port = parse_service_port(port)?;
    Ok(format!("{host}:{port}"))
}

fn main() {
    let endpoint = build_endpoint("127.0.0.1", "8080").expect("valid endpoint");
    assert_eq!(endpoint, "127.0.0.1:8080");

    println!("endpoint: {endpoint}");
    println!("run tests with: rustc --test tests-cover-success-and-failure.rs && ./tests-cover-success-and-failure");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_valid_port_with_whitespace() {
        assert_eq!(parse_service_port(" 8080 "), Ok(8080));
    }

    #[test]
    fn builds_endpoint_on_success_path() {
        assert_eq!(
            build_endpoint("api.example.test", "4430"),
            Ok("api.example.test:4430".to_string())
        );
    }

    #[test]
    fn rejects_empty_port() {
        assert_eq!(parse_service_port("   "), Err(PortError::Empty));
    }

    #[test]
    fn rejects_non_numeric_port() {
        assert!(matches!(parse_service_port("http"), Err(PortError::NotNumber)));
    }

    #[test]
    fn rejects_reserved_port_and_keeps_value() {
        assert_eq!(parse_service_port("80"), Err(PortError::Reserved(80)));
    }
}
```

**坑**：只测试 happy path，会让错误类型、边界值和 panic 在上线后才暴露；把错误统一转成字符串，也会让测试只能匹配文案，难以验证具体分支和关键数据。

**检查**：每个返回 `Result` 的核心函数，是否至少有一个成功用例、一个失败用例和一个边界用例？能否用结构化错误而不是字符串文案来断言失败原因？
