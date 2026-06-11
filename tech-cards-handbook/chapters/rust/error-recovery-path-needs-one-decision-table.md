# 错误恢复路径需要一张决策表串起来

**问题**：Rust 的 `Result`、错误枚举、`match`、重试策略、降级和对外错误码都很适合显式表达；但如果这些决策分散在 repository、service、handler 的多个 `match` 分支里，review 时仍然很难确认“这个错误到底应该重试、降级、返回用户可见错误，还是升级为内部故障”。

**要点**：

- 先把领域错误枚举稳定下来，再为每个错误登记默认恢复动作。
- 决策表里同时写 `action`、`retryable`、`degraded`、`public_code` 和 `public_message`，不要只写 HTTP status 或日志文本。
- 调用方可以根据业务语义把某个默认 `RETURN_PUBLIC_ERROR` 改成局部降级，但这个选择要返回可观测的 `degraded` 标记。
- 对外响应只读取安全字段；底层 host、trace、文件路径和驱动错误只保留在内部错误上下文里。

| 维度 | 零散 `match` | 决策表 |
|---|---|---|
| 错误分类 | 每层各自匹配 `AppError` | 领域错误枚举统一登记 |
| 恢复动作 | 重试、降级和 500 分散在调用链 | `RecoveryAction` 明确表达 |
| 对外契约 | handler 临时拼字符串 | `public_code` / `public_message` 稳定输出 |
| 审查方式 | 需要读完整调用链 | 一张表能发现缺口 |

**示例**：

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ErrorCode {
    ProfileNotFound,
    ProfileTemporarilyUnavailable,
    Internal,
}

impl ErrorCode {
    fn as_str(self) -> &'static str {
        match self {
            ErrorCode::ProfileNotFound => "PROFILE_NOT_FOUND",
            ErrorCode::ProfileTemporarilyUnavailable => "PROFILE_TEMPORARILY_UNAVAILABLE",
            ErrorCode::Internal => "INTERNAL_ERROR",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RecoveryAction {
    Retry,
    Degrade,
    ReturnPublicError,
    Escalate,
}

#[derive(Debug, Clone)]
struct AppError {
    code: ErrorCode,
    message: &'static str,
    source: &'static str,
}

#[derive(Debug, Clone, Copy)]
struct RecoveryDecision {
    action: RecoveryAction,
    public_code: ErrorCode,
    public_message: &'static str,
    retryable: bool,
    degraded: bool,
}

const DECISION_TABLE: &[(ErrorCode, RecoveryDecision)] = &[
    (
        ErrorCode::ProfileNotFound,
        RecoveryDecision {
            action: RecoveryAction::ReturnPublicError,
            public_code: ErrorCode::ProfileNotFound,
            public_message: "profile not found",
            retryable: false,
            degraded: false,
        },
    ),
    (
        ErrorCode::ProfileTemporarilyUnavailable,
        RecoveryDecision {
            action: RecoveryAction::Retry,
            public_code: ErrorCode::ProfileTemporarilyUnavailable,
            public_message: "profile service is temporarily unavailable",
            retryable: true,
            degraded: false,
        },
    ),
    (
        ErrorCode::Internal,
        RecoveryDecision {
            action: RecoveryAction::Escalate,
            public_code: ErrorCode::Internal,
            public_message: "internal server error",
            retryable: false,
            degraded: false,
        },
    ),
];

fn decide_recovery(error: &AppError) -> RecoveryDecision {
    DECISION_TABLE
        .iter()
        .find(|(code, _)| *code == error.code)
        .map(|(_, decision)| *decision)
        .unwrap_or(RecoveryDecision {
            action: RecoveryAction::Escalate,
            public_code: ErrorCode::Internal,
            public_message: "internal server error",
            retryable: false,
            degraded: false,
        })
}

fn display_name_or_degrade(error: &AppError) -> Result<(&'static str, RecoveryDecision), AppError> {
    if error.code != ErrorCode::ProfileNotFound {
        return Err(error.clone());
    }

    let base = decide_recovery(error);
    Ok((
        "anonymous",
        RecoveryDecision {
            action: RecoveryAction::Degrade,
            public_code: base.public_code,
            public_message: base.public_message,
            retryable: false,
            degraded: true,
        },
    ))
}

fn public_response(error: &AppError) -> String {
    let decision = decide_recovery(error);
    format!(
        "{{\"code\":\"{}\",\"message\":\"{}\"}}",
        decision.public_code.as_str(),
        decision.public_message
    )
}

fn translate_profile_error(source: &'static str) -> AppError {
    if source.contains("no rows") {
        AppError {
            code: ErrorCode::ProfileNotFound,
            message: "profile not found",
            source,
        }
    } else if source.contains("timeout") {
        AppError {
            code: ErrorCode::ProfileTemporarilyUnavailable,
            message: "profile temporarily unavailable",
            source,
        }
    } else {
        AppError {
            code: ErrorCode::Internal,
            message: "internal server error",
            source,
        }
    }
}

fn main() {
    let missing = translate_profile_error("sql: no rows in result set for profile_id=42");
    let (name, degraded_decision) = display_name_or_degrade(&missing).unwrap();
    assert_eq!(name, "anonymous");
    assert_eq!(degraded_decision.action, RecoveryAction::Degrade);
    assert!(degraded_decision.degraded);

    let temporary = translate_profile_error("profile sdk timeout: host=10.0.0.8 trace=abc");
    let retry_decision = decide_recovery(&temporary);
    assert_eq!(retry_decision.action, RecoveryAction::Retry);
    assert!(retry_decision.retryable);

    let response = public_response(&temporary);
    assert!(response.contains(ErrorCode::ProfileTemporarilyUnavailable.as_str()));
    assert!(!response.contains("10.0.0.8"));
    assert!(!response.contains("trace=abc"));
    assert!(temporary.source.contains("10.0.0.8"));
    assert_eq!(temporary.message, "profile temporarily unavailable");

    let corrupted = translate_profile_error("json decode failed at /var/lib/profiles/42.json");
    assert_eq!(decide_recovery(&corrupted).action, RecoveryAction::Escalate);
    assert!(!public_response(&corrupted).contains("/var/lib"));

    println!("error recovery decision table keeps Rust actions explicit");
}
```

**坑**：

- 只新增 `AppError` 变体，不更新决策表，导致新错误默认变成 500 或被调用方误判为可降级。
- 在 handler 里直接 `format!("{:?}", error)`，把 `source` 里的 host、trace、文件路径暴露到公开响应。
- 把重试写在一个 `loop` 里、降级写在另一个调用方里、对外错误码写在 adapter 里，审查时看不出三者是否一致。
- 用 `_ =>` 吞掉未来新增错误，编译器无法提醒你为新错误补恢复动作。

**检查**：

- 每个领域错误枚举是否都能在一张表里看到默认动作、是否可重试、是否可降级和对外错误码？
- 调用方做局部降级时，是否返回可观测的 `degraded` 标记，而不是静默返回默认值？
- 对外响应是否只读取决策表里的安全字段，不直接输出 `source` / `Debug` 字符串？
- 新增错误枚举或错误转换时，示例/测试是否能失败提示“决策表未覆盖”？

**延伸阅读**：

- Rust 显式重试：[`retry-strategy-explicit-not-implicit-loop.md`](retry-strategy-explicit-not-implicit-loop.md)
- Rust 调用方降级：[`degradation-strategy-at-caller-not-callee.md`](degradation-strategy-at-caller-not-callee.md)
- Rust 对外错误码：[`external-error-codes-domain-defined-not-leaked.md`](external-error-codes-domain-defined-not-leaked.md)
- Go 决策表对照：[`../go/error-recovery-path-needs-one-decision-table.md`](../go/error-recovery-path-needs-one-decision-table.md)
- Python 决策表对照：[`../python/error-recovery-path-needs-one-decision-table.md`](../python/error-recovery-path-needs-one-decision-table.md)
