# 所有权解决“谁负责释放资源”

**问题**：为什么 Rust 不需要垃圾回收也能管理内存？

**要点**：

- 每个值有且只有一个 owner。
- owner 离开作用域时值被释放。
- 赋值、传参可能发生 move。

**示例**：

```rust
fn consume(name: String) {
    println!("{name}");
}

let name = String::from("Ada");
consume(name);
// println!("{name}"); // name 已经被移动
```

**坑**：把 `String`、`Vec` 这类堆分配值传给函数后，原变量默认不能继续用。

**检查**：如果函数不需要拥有值，参数优先写成引用。
