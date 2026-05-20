# 模式匹配让分支覆盖更可靠

**问题**：如何避免漏处理某一种状态？

**要点**：

- `match` 会强制覆盖所有可能分支。
- 枚举适合表达有限状态集合。
- `_` 分支方便兜底，但也可能掩盖未来新增状态。

**示例**：

```rust
enum JobState {
    Queued,
    Running(u8),
    Failed(String),
    Done,
}

fn label(state: JobState) -> String {
    match state {
        JobState::Queued => "waiting".to_string(),
        JobState::Running(percent) => format!("running {percent}%"),
        JobState::Failed(reason) => format!("failed: {reason}"),
        JobState::Done => "done".to_string(),
    }
}
```

**坑**：在核心业务状态上过早使用 `_ => ...`，会让新增枚举变体时编译器无法提醒你补逻辑。

**检查**：新增一个枚举变体后，相关 `match` 是否能暴露需要修改的业务分支？
