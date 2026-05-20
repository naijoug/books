# `Result` 表达“可能失败且有原因”

**问题**：如何把错误从底层传到上层，同时保留失败原因？

**要点**：

- `Result<T, E>` 是成功值或错误值。
- `?` 用于向上传播错误。
- 应用层可以用统一错误类型，库层避免随意吞错误。

**示例**：

```rust
use std::fs;
use std::io;

fn load_config(path: &str) -> Result<String, io::Error> {
    let content = fs::read_to_string(path)?;
    Ok(content)
}
```

**坑**：把所有错误转成字符串会丢失类型信息，后续难以分类处理。

**检查**：调用方能否区分“文件不存在”“权限不足”“格式错误”？
