# 借用用于临时读取或修改

**问题**：函数只是看一眼数据，为什么要拿走所有权？

**要点**：

- `&T` 是不可变借用，可同时存在多个。
- `&mut T` 是可变借用，同一时间只能有一个。
- 可变借用期间不能再使用原变量做其他访问。

**示例**：

```rust
fn read_job_name(job: &String) -> usize {
    println!("reading job: {job}");
    job.len()
}

fn append_suffix(job: &mut String) {
    job.push_str("_done");
}

fn main() {
    let mut job = String::from("build");

    let first_read = read_job_name(&job);
    let second_read = read_job_name(&job);
    assert_eq!(first_read, second_read);

    // 不可变借用的最后一次使用已经结束，之后才能创建可变借用。
    append_suffix(&mut job);
    assert_eq!(job, "build_done");

    {
        let temporary = &mut job;
        temporary.push_str("_verified");
    } // 可变借用在这里结束，原变量重新可用。

    println!("final job: {job}");
    assert_eq!(job, "build_done_verified");
}
```

**坑**：同时持有不可变引用和可变引用会被拒绝。先缩短引用作用域，再修改。Rust 的非词法生命周期（NLL）会在引用最后一次使用后结束借用，但如果引用后面还要被使用，就不能提前创建 `&mut T`。

**检查**：编译器提示 borrow 冲突时，先问“这个引用真的需要活这么久吗？”优先用函数边界或小作用域表达“只是临时读/改一下”。
