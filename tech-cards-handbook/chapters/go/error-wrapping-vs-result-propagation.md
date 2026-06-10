# Go 错误包装与 Rust 错误传播的对照

**问题**：Go 的 `fmt.Errorf("%w", err)` 和 Rust 的 `?` 都能向上传递错误，但它们对调用方意味着什么？什么时候该包装，什么时候该转换？

**要点**：

- Go 用 `%w` 包装保留错误链，调用方通过 `errors.Is` / `errors.As` 判断根因；每一层补"做什么、对谁做"的上下文。
- Rust 用 `From<Inner>` + `?` 自动转换错误类型，调用方通过 `match` 分支判断错误类别；`Display` 实现补人类可读上下文。
- 两者的共同目标是：调用方能**分类处理**错误（重试、降级、返回用户友好消息），而不是只能打日志或 panic。
- 两者的共同陷阱是：把底层实现细节（OS error code、ORM driver error）原样泄露给上层，导致接口绑定具体实现。

| 维度 | Go | Rust |
|---|---|---|
| 传播方式 | `return fmt.Errorf("xxx: %w", err)` | `inner_result?`（需要 `From<Inner>`） |
| 错误链 | 保留在 `%w` 包装链中 | 编译期转换，旧类型被吃掉 |
| 分类方式 | `errors.Is` / `errors.As` | `match err { A => ..., B => ... }` |
| 上下文位置 | 包装时写字符串 | `Display` / `Error` 实现 |
| 编译保障 | 无；忘写 `%w` 就断链 | 有；`?` 要求 `From` 或类型匹配 |

**示例 — Go 侧**：

```go
package main

import (
	"errors"
	"fmt"
	"os"
	"strings"
)

// 领域错误，不暴露底层是文件还是数据库
type NotFoundError struct {
	Resource string
	Key      string
}

func (e *NotFoundError) Error() string {
	return fmt.Sprintf("%s not found: %s", e.Resource, e.Key)
}

func findUser(name string) (*string, error) {
	data, err := os.ReadFile("users.txt")
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, &NotFoundError{Resource: "user", Key: name}
		}
		return nil, fmt.Errorf("find user %s: %w", name, err)
	}
	for _, line := range strings.Split(string(data), "\n") {
		if strings.TrimSpace(line) == name {
			return &name, nil
		}
	}
	return nil, &NotFoundError{Resource: "user", Key: name}
}

func main() {
	_, err := findUser("alice")
	if err == nil {
		panic("expected not found error")
	}

	var notFound *NotFoundError
	if errors.As(err, &notFound) {
		fmt.Printf("domain error: %s (resource=%s key=%s)\n", notFound.Error(), notFound.Resource, notFound.Key)
	} else {
		panic(fmt.Sprintf("unexpected error: %v", err))
	}
}
```

**示例 — Rust 侧**：

```rust
use std::fmt;
use std::fs;
use std::io;

// 领域错误，不暴露底层是文件系统还是数据库
#[derive(Debug)]
enum FindUserError {
    Io(io::Error),
    NotFound { name: String },
}

impl From<io::Error> for FindUserError {
    fn from(error: io::Error) -> Self {
        FindUserError::Io(error)
    }
}

impl fmt::Display for FindUserError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            FindUserError::Io(e) => write!(f, "find user failed: {e}"),
            FindUserError::NotFound { name } => write!(f, "user not found: {name}"),
        }
    }
}

fn find_user(name: &str) -> Result<String, FindUserError> {
    let content = fs::read_to_string("users.txt")?;
    if content.lines().any(|line| line.trim() == name) {
        Ok(name.to_string())
    } else {
        Err(FindUserError::NotFound { name: name.to_string() })
    }
}

fn main() {
    match find_user("alice") {
        Ok(user) => println!("found: {user}"),
        Err(FindUserError::NotFound { name }) => {
            println!("domain error: user not found ({name})");
        }
        Err(FindUserError::Io(e)) => {
            println!("io error: {e}");
        }
    }
}
```

**坑**：

- Go：`fmt.Errorf("failed: %v", err)` 用 `%v` 而不是 `%w`，错误链断裂，`errors.Is` 失效。
- Rust：`From` 实现如果不区分"文件不存在"和"权限不足"，调用方 `match` 到的都是同一个变体，丢失了重试条件。
- 两者共同：如果领域层直接返回 `os.ErrNotExist` / `io::ErrorKind::NotFound`，上层就会绑定文件系统语义；下次把存储换成 Redis 或 gRPC，所有 `errors.Is(err, os.ErrNotExist)` / `match io::ErrorKind::NotFound` 都要改。

**检查**：

- Go：`errors.Is` 能否命中你期望的根因？`%w` 是否写对了？领域错误是否隐藏了底层是文件、数据库还是网络？
- Rust：`match` 能否区分"可重试"和"不可重试"？`From` 实现是否把不同底层错误映射到不同的领域变体？`Display` 输出是否包含"做什么、对谁做"？
