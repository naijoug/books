# 模块边界控制可见性

**问题**：如何让内部实现可以重构，而不影响调用方？

**要点**：

- Rust 默认私有；只有显式 `pub` 的类型、函数或字段才会成为外部可见 API。
- `pub(crate)` 适合 crate 内部协作：同一个 crate 的其他模块可以复用，但 crate 外调用方不能依赖它。
- 结构体本身 `pub` 不代表字段也公开；优先用构造函数和方法维护不变量。
- 对外 API 越小，内部重命名、拆模块、替换实现的成本越低。

**示例**：

```rust
mod sdk {
    #[derive(Debug, PartialEq, Eq)]
    pub struct Client {
        endpoint: String,
        token: Secret,
    }

    #[derive(Debug, PartialEq, Eq)]
    struct Secret(String);

    impl Client {
        pub fn new(endpoint: impl Into<String>, token: impl Into<String>) -> Self {
            Self {
                endpoint: endpoint.into(),
                token: Secret(token.into()),
            }
        }

        pub fn send(&self, body: &str) -> String {
            let signature = self.sign(body);
            transport::post(&self.endpoint, body, &signature)
        }

        pub(crate) fn audit_label(&self) -> String {
            format!("client:{}", self.endpoint)
        }

        fn sign(&self, body: &str) -> String {
            format!("sig:{}:{}", self.token.0.len(), body.len())
        }
    }

    mod transport {
        pub(super) fn post(endpoint: &str, body: &str, signature: &str) -> String {
            format!("POST {endpoint} body={body} {signature}")
        }
    }
}

fn main() {
    let client = sdk::Client::new("https://api.example.test", "secret-token");

    let response = client.send("hello");
    assert_eq!(
        response,
        "POST https://api.example.test body=hello sig:12:5"
    );

    // `pub(crate)` 暴露给同一个 crate 的其他模块，适合内部审计、测试或编排。
    assert_eq!(client.audit_label(), "client:https://api.example.test");

    // 下面这些访问应当保持不可编译，说明实现细节没有泄漏成公开 API：
    // client.endpoint;
    // client.sign("hello");
    // sdk::transport::post("/", "body", "sig");

    println!("{}", client.audit_label());
    println!("module visibility demo done");
}
```

如果把上面注释中的私有字段、私有方法或私有子模块访问打开，编译器会报类似错误：

```text
error[E0616]: field `endpoint` of struct `Client` is private
error[E0624]: method `sign` is private
error[E0603]: module `transport` is private
```

**坑**：为了测试方便把所有函数都改成 `pub`，会把临时实现变成长期 API 负担。更好的做法是把“需要被同 crate 复用”的能力标成 `pub(crate)`，把真正跨 crate 稳定承诺的接口限制在少数 `pub` 类型和方法上。

**检查**：这个函数是否真的需要被 crate 外调用？如果不是，先保持私有或 `pub(crate)`；这个字段是否必须让调用方直接读写？如果不是，用构造函数和方法表达不变量。
