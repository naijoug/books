# 借用用于临时读取或修改

**问题**：函数只是看一眼数据，为什么要拿走所有权？

**要点**：

- `&T` 是不可变借用，可同时存在多个。
- `&mut T` 是可变借用，同一时间只能有一个。
- 可变借用期间不能再使用原变量做其他访问。

**示例**：

```rust
fn append_suffix(input: &mut String) {
    input.push_str("_done");
}

let mut job = String::from("build");
append_suffix(&mut job);
println!("{job}");
```

**坑**：同时持有不可变引用和可变引用会被拒绝。先缩短引用作用域，再修改。

**检查**：编译器提示 borrow 冲突时，先问“这个引用真的需要活这么久吗？”
