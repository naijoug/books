# 迭代器让数据转换更可组合

**问题**：如何写出清晰的数据过滤、转换和聚合逻辑？

**要点**：

- `iter()` 借用元素，`into_iter()` 消费集合。
- `map` 转换，`filter` 过滤，`collect` 收集。
- 链式迭代器是惰性的，直到消费时才执行。

**示例**：

```rust
let names = vec!["ada", "grace", "linus"];

let labels: Vec<String> = names
    .iter()
    .filter(|name| name.len() >= 4)
    .map(|name| name.to_uppercase())
    .collect();

assert_eq!(labels, vec!["GRACE", "LINUS"]);
```

**坑**：`into_iter()` 会移动集合所有权。后面还要继续使用原集合时，优先用 `iter()`。

**检查**：链式调用最后是否有消费操作，如 `collect`、`sum`、`count` 或 `for_each`？
