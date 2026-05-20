# trait 表达行为契约

**问题**：如何让不同类型共享一组能力？

**要点**：

- trait 定义方法集合。
- 泛型参数加 trait bound 可以获得静态分发。
- `dyn Trait` 用于运行时多态。

**示例**：

```rust
trait Render {
    fn render(&self) -> String;
}

struct Button {
    label: String,
}

impl Render for Button {
    fn render(&self) -> String {
        format!("<button>{}</button>", self.label)
    }
}
```

**坑**：不要把 trait 设计成“万能服务接口”。小 trait 更容易组合和测试。

**检查**：这个 trait 是否表达了稳定行为，而不是临时为了 mock 抽出来的对象？
