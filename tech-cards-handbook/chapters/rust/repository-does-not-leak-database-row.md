# Repository 不要把数据库 row 泄漏到领域层

## 什么时候用

当 repository 方法直接返回 `UserRow`、`OrderRecord`、`sqlx::FromRow` 这类持久化结构，然后让 service / use case 自己解释列名、软删除字段、审计字段或密码 hash 时。数据库 row 表达存储契约，领域模型表达业务不变量，二者变化原因不同。

## 怎么写

```rust
use std::convert::TryFrom;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct UserId(i64);

#[derive(Clone, Debug, PartialEq, Eq)]
struct EmailAddress(String);

#[derive(Clone, Debug, PartialEq, Eq)]
struct DisplayName(String);

#[derive(Clone, Debug, PartialEq, Eq)]
struct User {
    id: UserId,
    email: EmailAddress,
    display_name: DisplayName,
    active: bool,
}

#[derive(Clone, Debug)]
struct UserRow {
    id: i64,
    email: String,
    display_name: String,
    password_hash: String,
    deleted_at: Option<String>,
}

#[derive(Debug, PartialEq, Eq)]
enum RepositoryError {
    NotFound,
    InvalidRow(&'static str),
}

impl TryFrom<UserRow> for User {
    type Error = RepositoryError;

    fn try_from(row: UserRow) -> Result<Self, Self::Error> {
        if row.id <= 0 {
            return Err(RepositoryError::InvalidRow("user id must be positive"));
        }
        if !row.email.contains('@') {
            return Err(RepositoryError::InvalidRow("email is invalid"));
        }
        if row.display_name.trim().is_empty() {
            return Err(RepositoryError::InvalidRow("display name is empty"));
        }

        Ok(User {
            id: UserId(row.id),
            email: EmailAddress(row.email.to_lowercase()),
            display_name: DisplayName(row.display_name.trim().to_owned()),
            active: row.deleted_at.is_none(),
        })
    }
}

trait UserRepository {
    fn find_by_id(&self, id: UserId) -> Result<User, RepositoryError>;
}

struct InMemoryUserRepository {
    rows: Vec<UserRow>,
}

impl UserRepository for InMemoryUserRepository {
    fn find_by_id(&self, id: UserId) -> Result<User, RepositoryError> {
        let row = self
            .rows
            .iter()
            .find(|row| row.id == id.0)
            .cloned()
            .ok_or(RepositoryError::NotFound)?;

        User::try_from(row)
    }
}

#[derive(Debug, PartialEq, Eq)]
struct PublicProfile {
    id: i64,
    email: String,
    display_name: String,
    active: bool,
}

fn to_public_profile(user: &User) -> PublicProfile {
    PublicProfile {
        id: user.id.0,
        email: user.email.0.clone(),
        display_name: user.display_name.0.clone(),
        active: user.active,
    }
}

fn main() {
    let repository = InMemoryUserRepository {
        rows: vec![UserRow {
            id: 42,
            email: "ADA@EXAMPLE.COM".to_owned(),
            display_name: " Ada ".to_owned(),
            password_hash: "argon2$secret".to_owned(),
            deleted_at: None,
        }],
    };

    let user = repository.find_by_id(UserId(42)).expect("user exists");
    let profile = to_public_profile(&user);

    assert_eq!(profile.id, 42);
    assert_eq!(profile.email, "ada@example.com");
    assert_eq!(profile.display_name, "Ada");
    assert!(profile.active);
    assert!(!format!("{:?}", profile).contains("argon2$secret"));

    println!("{}:{}", profile.id, profile.email);
}
```

## 哪里容易错

1. **repository trait 返回 `UserRow`**：调用方会到处读取列名，业务层被迫知道 `deleted_at`、`password_hash`、`updated_at` 这些存储细节。
2. **用 `From<UserRow> for User` 包装可能失败的转换**：row 里的脏数据、历史迁移数据或空字段都可能让领域不变量不成立，应该用 `TryFrom` / 显式 mapper 返回 `Result`。
3. **把数据库字段直接带到 API DTO**：持久化结构里常有密码 hash、审计字段、软删除字段和内部状态，必须先进入领域模型，再按输出边界生成 DTO。
4. **为了查询方便改领域模型**：不要让 `Option<String>`、数据库默认值或 nullable 列反向决定领域对象的公开字段；在 repository adapter 层做兼容和校验。

## 一句话总结

Repository 的公开接口应该返回领域模型和领域可理解的错误；数据库 row 只存在于 adapter 内部，离开存储边界前必须完成验证、清洗和字段裁剪。
