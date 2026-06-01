# 模式匹配让分支覆盖更可靠

**问题**：如何避免漏处理某一种状态？

**要点**：

- `match` 会强制覆盖所有可能分支；没有覆盖完整时，代码无法编译。
- 枚举适合表达有限状态集合；每个变体可以携带不同形状的数据。
- `if let` / `matches!` 适合只关心少数分支；核心业务状态优先用显式 `match`。
- `_` 分支方便兜底，但也可能掩盖未来新增状态。

**示例**：

```rust
#[derive(Debug, PartialEq, Eq)]
enum JobState {
    Queued,
    Running { percent: u8, worker: String },
    Failed(String),
    Done,
    Cancelled { by: String },
}

fn label(state: &JobState) -> String {
    match state {
        JobState::Queued => "waiting".to_string(),
        JobState::Running { percent, worker } => {
            format!("running {percent}% on {worker}")
        }
        JobState::Failed(reason) => format!("failed: {reason}"),
        JobState::Done => "done".to_string(),
        JobState::Cancelled { by } => format!("cancelled by {by}"),
    }
}

fn should_retry(state: &JobState) -> bool {
    match state {
        JobState::Failed(reason) if reason.contains("timeout") => true,
        JobState::Failed(_) => false,
        JobState::Queued | JobState::Running { .. } | JobState::Done | JobState::Cancelled { .. } => false,
    }
}

fn main() {
    let states = vec![
        JobState::Queued,
        JobState::Running {
            percent: 42,
            worker: "agent-7".to_string(),
        },
        JobState::Failed("network timeout".to_string()),
        JobState::Done,
        JobState::Cancelled {
            by: "operator".to_string(),
        },
    ];

    let labels: Vec<String> = states.iter().map(label).collect();

    assert_eq!(labels[0], "waiting");
    assert_eq!(labels[1], "running 42% on agent-7");
    assert_eq!(labels[2], "failed: network timeout");
    assert_eq!(labels[3], "done");
    assert_eq!(labels[4], "cancelled by operator");

    assert!(should_retry(&states[2]));
    assert!(matches!(states[3], JobState::Done));

    if let JobState::Running { percent, worker } = &states[1] {
        println!("active job: {percent}% on {worker}");
    }

    for label in labels {
        println!("{label}");
    }
}
```

**坑**：在核心业务状态上过早使用 `_ => ...`，会让新增枚举变体时编译器无法提醒你补逻辑。`_` 更适合协议边界、日志降级、确实不关心细节的展示层；在领域逻辑中，宁可把每个变体写出来，让编译器成为变更清单。

**检查**：新增一个枚举变体后，相关 `match` 是否能暴露需要修改的业务分支？如果没有任何编译错误，检查是不是 `_` 或过宽的 `..` 把真实分支吞掉了。
