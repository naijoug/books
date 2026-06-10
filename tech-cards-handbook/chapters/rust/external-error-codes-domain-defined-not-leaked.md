# 对外错误码应由领域定义，而不是从基础设施泄漏

## 问题

当 service 需要向调用方（HTTP client、CLI、前端、消息队列消费者）返回错误码时，常见的做法是直接透传数据库驱动错误码、HTTP status text 或第三方 SDK 错误字符串。这会导致：

1. 对外契约随底层实现变化——换数据库或换 HTTP client 后，调用方原来匹配的错误码就失效了。
2. 内部诊断信息暴露给外部——SQL state、文件路径、SDK 内部类型名被调用方看到。
3. 调用方无法稳定分类错误——同一个"用户不存在"在不同路径下可能分别返回 `sqlx::Error::RowNotFound`、`404 Not Found` 和 `"record not found"`。

## 要点

1. **领域错误枚举是唯一对外错误来源。** 调用方看到的是领域错误码（`USER_NOT_FOUND`、`INVALID_EMAIL`、`SERVICE_OVERLOADED`），不是 SQL state 或驱动类型名。
2. **adapter 负责把基础设施错误翻译成领域错误。** 数据库、HTTP client、文件系统、队列的底层错误在 adapter 里被 `match` / `map_err` 成领域错误；上层只看到领域枚举。
3. **对外错误码有三个字段就够了：** `code`（领域错误码）、`message`（用户可见描述）、`trace_id`（可关联日志的追踪标识）。底层错误细节只进日志，不进响应。
4. **领域错误码要稳定、有文档、可枚举。** 不要用 `format!("db error: {}", e)` 这种动态拼接；错误码是一个枚举值，API 变更时应走版本化。

## 示例

```rust
// --- 领域错误枚举 ---

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DomainError {
    UserNotFound { user_id: String },
    InvalidEmail { value: String, reason: String },
    ServiceOverloaded { retry_after_secs: u32 },
    Internal { trace_id: String },
}

impl DomainError {
    /// 对外错误码：稳定、可枚举、调用方可 match
    pub fn code(&self) -> &'static str {
        match self {
            DomainError::UserNotFound { .. } => "USER_NOT_FOUND",
            DomainError::InvalidEmail { .. } => "INVALID_EMAIL",
            DomainError::ServiceOverloaded { .. } => "SERVICE_OVERLOADED",
            DomainError::Internal { .. } => "INTERNAL_ERROR",
        }
    }

    /// 用户可见描述：不含底层错误字符串或文件路径
    pub fn message(&self) -> String {
        match self {
            DomainError::UserNotFound { user_id } => {
                format!("用户 {} 不存在", user_id)
            }
            DomainError::InvalidEmail { value, reason } => {
                format!("邮箱地址 '{}' 无效：{}", value, reason)
            }
            DomainError::ServiceOverloaded { retry_after_secs } => {
                format!("服务繁忙，请 {} 秒后重试", retry_after_secs)
            }
            DomainError::Internal { trace_id } => {
                format!("内部错误，请联系支持（追踪号 {}）", trace_id)
            }
        }
    }
}

// --- adapter 把底层错误翻译成领域错误 ---

#[derive(Debug)]
pub enum DbError {
    RowNotFound,
    UniqueViolation { column: String },
    ConnectionTimeout,
    Other(String),
}

fn find_user_by_id(user_id: &str, db_result: Result<String, DbError>) -> Result<String, DomainError> {
    db_result.map_err(|e| match e {
        DbError::RowNotFound => DomainError::UserNotFound {
            user_id: user_id.to_string(),
        },
        DbError::UniqueViolation { column } => DomainError::InvalidEmail {
            value: user_id.to_string(),
            reason: format!("{} 已被占用", column),
        },
        DbError::ConnectionTimeout => DomainError::ServiceOverloaded {
            retry_after_secs: 30,
        },
        DbError::Other(msg) => {
            // 底层细节只进日志，不进对外响应
            eprintln!("[internal] db error for user {}: {}", user_id, msg);
            DomainError::Internal {
                trace_id: format!("trace-{}", user_id.len()),
            }
        }
    })
}

// --- 调用方只看到领域错误 ---

fn main() {
    let cases = vec![
        (Ok("Alice Johnson".to_string()), "alice"),
        (Err(DbError::RowNotFound), "bob"),
        (Err(DbError::UniqueViolation { column: "email".to_string() }), "charlie"),
        (Err(DbError::ConnectionTimeout), "dave"),
        (Err(DbError::Other("connection pool exhausted".to_string())), "eve"),
    ];

    for (db_result, user_id) in cases {
        match find_user_by_id(user_id, db_result) {
            Ok(name) => println!("found: {}", name),
            Err(e) => println!("code={}, message={}", e.code(), e.message()),
        }
    }
}
```

输出：

```
found: Alice Johnson
code=USER_NOT_FOUND, message=用户 bob 不存在
code=INVALID_EMAIL, message=邮箱地址 'charlie' 无效：email 已被占用
code=SERVICE_OVERLOADED, message=服务繁忙，请 30 秒后重试
[internal] db error for user eve: connection pool exhausted
code=INTERNAL_ERROR, message=内部错误，请联系支持（追踪号 3）
```

## 坑

1. **直接把 `sqlx::Error` / `reqwest::Error` 序列化成 JSON 返回。** 调用方看到的是 Rust crate 内部类型名和版本敏感的字段，换库就断了。
2. **用 `format!("{}", e)` 做错误码。** 底层错误字符串会随驱动版本、操作系统 locale 变化，不可 match。
3. **在领域层 import 数据库驱动类型来做错误分类。** 这让领域层反向依赖基础设施，违反 adapter 边界。
4. **所有错误都返回 `500 Internal Server Error`。** 调用方无法区分"请求参数错"和"服务端暂时过载"，也没法做客户端重试或降级。

## 检查

- [ ] 对外响应中的 `code` 字段值都来自领域枚举的 `match` 分支，没有动态拼接或底层类型名。
- [ ] 每个领域错误码都有文档说明调用方应采取的动作（重试 / 修改参数 / 放弃）。
- [ ] adapter 层的 `map_err` 把所有已知的底层错误都映射成了领域错误；未知错误走 `Internal` + 日志。
- [ ] `message` 字段不含文件路径、SQL 语句、连接字符串或驱动类型名。
