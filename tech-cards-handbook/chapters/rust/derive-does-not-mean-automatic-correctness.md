# derive 不等于自动正确

**问题**：Rust 的 `#[derive(Debug, Clone, PartialEq, Eq, Hash)]` 很方便，但哪些 trait 应该派生、哪些必须手写？如果给领域类型一口气派生所有 trait，可能把“调试打印”“相等判断”“可复制”这些语义都默认成底层字段行为。

**要点**：

- `derive` 是语义承诺，不只是省代码；派生前先问这个 trait 是否符合领域规则。
- `Debug` 可能泄露敏感字段，必要时手写并打码。
- `PartialEq` / `Eq` 的默认行为是逐字段比较；如果业务相等性只看归一化后的值，应手写实现。
- `Clone` / `Copy` 会降低所有权提醒强度；对 token、连接、句柄这类资源要谨慎。
- newtype 默认不会继承内部类型的 trait，正好给你一个显式选择边界。

**示例**：

```rust
use std::fmt;

struct EmailAddress(String);

impl EmailAddress {
    fn parse(input: &str) -> Option<Self> {
        let normalized = input.trim().to_ascii_lowercase();
        if normalized.contains('@') {
            Some(Self(normalized))
        } else {
            None
        }
    }
}

// 调试输出只暴露安全信息，不打印完整邮箱。
impl fmt::Debug for EmailAddress {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let domain = self.0.split('@').nth(1).unwrap_or("unknown");
        f.debug_struct("EmailAddress")
            .field("domain", &domain)
            .finish()
    }
}

// 业务相等性基于 parse 后的规范化值，而不是原始输入字符串。
impl PartialEq for EmailAddress {
    fn eq(&self, other: &Self) -> bool {
        self.0 == other.0
    }
}

impl Eq for EmailAddress {}

fn same_account(left: &EmailAddress, right: &EmailAddress) -> bool {
    left == right
}

fn main() {
    let a = EmailAddress::parse(" Alice@Example.COM ").expect("valid email");
    let b = EmailAddress::parse("alice@example.com").expect("valid email");

    assert!(same_account(&a, &b));
    assert_eq!(format!("{:?}", a), "EmailAddress { domain: \"example.com\" }");

    // 如果直接 #[derive(Debug, PartialEq)] 并保存原始输入：
    // - Debug 会打印完整邮箱；
    // - PartialEq 会把大小写、空格差异误判为不同账户。
}
```

**坑**：最常见的反模式是为了让测试或集合 API 快速通过，给领域类型统一加 `#[derive(Debug, Clone, PartialEq, Eq, Hash)]`。这会把底层字段结构暴露成公开语义：以后字段一变，比较、日志、哈希和复制行为都跟着变。先把输入规范化、敏感输出、相等性和资源所有权想清楚，再决定 derive 还是手写。

**检查**：看到 `derive` 时逐项复核：这个类型能安全 `Debug` 吗？`Clone` 是否会复制不该复制的资源？`PartialEq` 是否就是逐字段相等？`Hash` 是否与相等性一致？如果任何答案不确定，先手写 trait 或暂时不实现。
