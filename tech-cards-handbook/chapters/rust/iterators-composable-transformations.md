# 迭代器让数据转换更可组合

**问题**：如何写出清晰的数据过滤、转换和聚合逻辑？

**要点**：

- `iter()` 借用元素，适合“读一遍但之后还要继续用原集合”的场景。
- `into_iter()` 消费集合，适合把元素所有权交给下一步转换或收集。
- `map` 转换，`filter` 过滤，`collect` 收集；链式迭代器是惰性的，直到 `collect`、`sum`、`count`、`for` 等消费操作才真正执行。

**示例**：

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
struct User {
    name: String,
    score: u32,
    active: bool,
}

fn active_labels(users: &[User]) -> Vec<String> {
    users
        .iter()
        .filter(|user| user.active && user.score >= 80)
        .map(|user| format!("{}:{}", user.name.to_uppercase(), user.score))
        .collect()
}

fn consume_names(users: Vec<User>) -> Vec<String> {
    users
        .into_iter()
        .filter(|user| user.active)
        .map(|user| user.name)
        .collect()
}

fn main() {
    let users = vec![
        User {
            name: String::from("ada"),
            score: 92,
            active: true,
        },
        User {
            name: String::from("grace"),
            score: 70,
            active: true,
        },
        User {
            name: String::from("linus"),
            score: 88,
            active: false,
        },
        User {
            name: String::from("barbara"),
            score: 95,
            active: true,
        },
    ];

    let labels = active_labels(&users);
    assert_eq!(labels, vec!["ADA:92", "BARBARA:95"]);

    // `iter()` 只借用元素，原集合仍然可继续使用。
    assert_eq!(users.len(), 4);

    let total_active_score: u32 = users
        .iter()
        .filter(|user| user.active)
        .map(|user| user.score)
        .sum();
    assert_eq!(total_active_score, 257);

    // `into_iter()` 消费集合，适合把每个 User 的 name 所有权拿出来。
    let active_names = consume_names(users);
    assert_eq!(active_names, vec!["ada", "grace", "barbara"]);

    // 到这里不能再使用 users：它已经被移动进 consume_names。
    println!("labels: {}", labels.join(", "));
    println!("active names: {}", active_names.join(", "));
    println!("iterator demo done");
}
```

**坑**：

- `into_iter()` 会移动集合所有权。后面还要继续使用原集合时，优先用 `iter()`；如果只想修改元素，用 `iter_mut()`。
- 只写 `map` / `filter` 不会立刻执行逻辑；必须接上 `collect`、`sum`、`count`、`for_each` 或 `for` 循环等消费步骤。
- 链很长时不要为了“函数式”牺牲可读性，可以把中间判断抽成有名字的小函数。

**检查**：链式调用最后是否有消费操作？当前链路是在借用元素、修改元素，还是消费元素所有权？
