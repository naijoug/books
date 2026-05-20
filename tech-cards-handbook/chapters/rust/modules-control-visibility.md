# 模块边界控制可见性

**问题**：如何让内部实现可以重构，而不影响调用方？

**要点**：

- 默认私有，`pub` 才对外暴露。
- `pub(crate)` 只在当前 crate 内可见。
- 对外 API 越小，后续重构越容易。

**示例**：

```rust
pub struct Client {
    token: String,
}

impl Client {
    pub fn new(token: String) -> Self {
        Self { token }
    }

    pub fn send(&self, body: &str) {
        self.sign_and_post(body);
    }

    fn sign_and_post(&self, body: &str) {
        println!("send {body} with token {}", self.token);
    }
}
```

**坑**：为了测试方便把所有函数都改成 `pub`，会把临时实现变成长期 API 负担。

**检查**：这个函数是否真的需要被 crate 外调用？如果不是，先保持私有。
