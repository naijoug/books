# newtype 把领域概念从原始类型里拆出来

**问题**：`UserId`、`OrderId`、`ProductId` 在底层都是 `u64`，Rust 不会阻止你把 `UserId` 传给期望 `OrderId` 的函数。怎么在编译期就捕获这类"同结构不同语义"的混用？

**要点**：

- newtype 用一个单字段 tuple struct 把原始类型包装成独立类型，零运行时开销。
- 编译器把 `struct UserId(u64)` 和 `struct OrderId(u64)` 视为完全不同的类型，传错会直接报错。
- newtype 可以显式实现需要的 trait（`Display`、`FromStr`、`Serialize`），只暴露业务允许的操作，不继承原始类型的全部行为。
- 不要为了省事直接用 type alias（`type UserId = u64`）；alias 只是别名，编译器不会阻止混用。

**示例**：

```rust
use std::fmt;

// 领域 ID：编译器把它们当成不同类型。
struct UserId(u64);
struct OrderId(u64);

impl UserId {
    fn new(id: u64) -> Self {
        Self(id)
    }
}

impl OrderId {
    fn new(id: u64) -> Self {
        Self(id)
    }
}

impl fmt::Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "user:{}", self.0)
    }
}

impl fmt::Display for OrderId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "order:{}", self.0)
    }
}

// 业务函数只接受具体类型，传错 u64 或别的 ID 编译不过。
fn load_user(id: UserId) -> String {
    format!("loading {}", id)
}

fn load_order(id: OrderId) -> String {
    format!("loading {}", id)
}

fn main() {
    let uid = UserId::new(42);
    let oid = OrderId::new(42);

    // 正确调用。注意 UserId/OrderId 没有 Copy，需要按引用或复制值。
    assert_eq!(load_user(UserId::new(42)), "loading user:42");
    assert_eq!(load_order(OrderId::new(42)), "loading order:42");

    // 以下代码编译失败，注释掉以保持示例可运行：
    // load_user(OrderId::new(42)); // mismatched types: expected UserId, found OrderId
    // load_order(42);             // mismatched types: expected OrderId, found integer

    // Display 按领域格式输出，不会裸露原始数值。
    println!("{}", UserId::new(42)); // user:42
    println!("{}", OrderId::new(42)); // order:42
}
```

**坑**：newtype 不会自动继承原始类型的 trait。如果需要比较或运算，要显式派生或实现（`#[derive(Debug, Clone, PartialEq)]` 或手动 `impl Eq`）。这是优点不是缺点——它让你只暴露业务真正需要的操作。另一个常见错误是在 API 边界直接 `.0` 取出原始值再传递，这会在边界处重新引入混用风险；优先让 newtype 贯穿整个调用链。

**检查**：你的代码库里有没有函数接受裸 `u64` / `String` / `i32` 但实际只代表一种领域概念？如果有，用 newtype 包起来，让编译器帮你守边界。
