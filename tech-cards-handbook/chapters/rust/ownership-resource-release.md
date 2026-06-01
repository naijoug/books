# 所有权解决"谁负责释放资源"

**问题**：为什么 Rust 不需要垃圾回收也能管理内存？

**要点**：

- 每个值有且只有一个 owner。
- owner 离开作用域时值被释放（`Drop` 自动调用）。
- 赋值、传参默认发生 move，原变量不再可用。
- `Clone` 可以显式深拷贝，但需要主动调用。

**示例**：

```rust
/// 演示所有权三件事：move 后原变量不可用、作用域结束时自动释放、
/// Clone 可以显式复制。
fn main() {
    // 1. move：传参后原变量不再可用
    let name = String::from("Ada");
    consume(name);
    // 取消下面这行注释会导致编译错误：borrow of moved value `name`
    // println!("{name}");

    // 2. Clone：显式深拷贝，两个变量各自独立
    let original = String::from("Grace");
    let clone = original.clone();
    println!("original={original}, clone={clone}");

    // 3. 作用域结束自动释放
    {
        let scoped = String::from("temporary");
        println!("inside scope: {scoped}");
    }
    // scoped 在这里已经被释放，不能再使用

    println!("ownership demo done");
}

fn consume(name: String) {
    println!("consumed: {name}");
}
```

**坑**：把 `String`、`Vec` 这类堆分配值传给函数后，原变量默认不能继续用。如果只是临时看一下，用引用 `&T` 而不是 move。

**检查**：如果函数不需要拥有值，参数优先写成引用。
