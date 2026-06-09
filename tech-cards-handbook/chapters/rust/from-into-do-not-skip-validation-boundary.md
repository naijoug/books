# From/Into 不要跨越业务验证边界

**问题**：Rust 的 `From` / `Into` 很适合表达无失败转换，但如果把外部字符串直接 `into()` 成 `EmailAddress`、`Money` 或 `UserId`，业务验证就会被藏进“看起来不会失败”的 API。什么时候该用 `From`，什么时候必须用 `TryFrom` 或显式构造函数？

**要点**：

- `From<T>` / `Into<T>` 应只用于不会失败、不会丢信息、不会改变业务语义的转换。
- 需要检查格式、范围、权限、唯一性或外部状态时，不要实现 `From`；用 `TryFrom`、`FromStr` 或 `new(...) -> Result<_, _>`。
- 外部 DTO、命令行参数、环境变量和数据库字符串先停在 adapter 边界，验证通过后再进入领域 newtype。
- `From` 可以用于领域类型到展示/持久化原始值的安全降级，但不要让它绕过领域入口。

**示例**：

```rust
use std::convert::TryFrom;
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
struct EmailAddress(String);

#[derive(Debug, Clone, PartialEq, Eq)]
enum EmailError {
    MissingAt,
    EmptyLocalPart,
    EmptyDomain,
}

impl fmt::Display for EmailAddress {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl TryFrom<&str> for EmailAddress {
    type Error = EmailError;

    fn try_from(raw: &str) -> Result<Self, Self::Error> {
        let trimmed = raw.trim().to_ascii_lowercase();
        let (local, domain) = trimmed.split_once('@').ok_or(EmailError::MissingAt)?;

        if local.is_empty() {
            return Err(EmailError::EmptyLocalPart);
        }
        if domain.is_empty() {
            return Err(EmailError::EmptyDomain);
        }

        Ok(Self(trimmed))
    }
}

impl From<EmailAddress> for String {
    fn from(email: EmailAddress) -> Self {
        email.0
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct RegisterUserCommand {
    email: EmailAddress,
}

fn command_from_request(email: &str) -> Result<RegisterUserCommand, EmailError> {
    Ok(RegisterUserCommand {
        email: EmailAddress::try_from(email)?,
    })
}

fn main() {
    let command = command_from_request(" Alice@Example.COM ").expect("valid email");
    assert_eq!(command.email.to_string(), "alice@example.com");

    let stored: String = command.email.into();
    assert_eq!(stored, "alice@example.com");

    assert_eq!(command_from_request("alice.example.com"), Err(EmailError::MissingAt));
    assert_eq!(command_from_request("@example.com"), Err(EmailError::EmptyLocalPart));

    // 不要这样实现：它会让任意字符串都能 .into() 成领域类型。
    // impl From<String> for EmailAddress { ... }
}
```

**坑**：为了让调用处少写 `?`，把 `String -> EmailAddress` 实现成 `From<String>`，等于告诉编译器“这个转换永远合法”。后续任何 adapter、测试 helper 或批处理脚本都能绕过验证制造非法领域值。另一个坑是把验证藏在 `From` 里然后 `panic!`；`From` 的语义仍然是无失败转换，失败应写进返回类型。

**检查**：搜索 `impl From<...> for <DomainNewtype>`、`.into()` 和 `as` 转换。只要转换跨越外部输入到领域模型，并且可能失败或改变语义，就改成 `TryFrom` / `FromStr` / `new(...) -> Result<_, _>`，并补一个失败用例。
