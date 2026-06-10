# 降级策略要在调用方实现，而不是在被调方隐藏

## 一句话

当被依赖服务不可用或超时时，降级决策（返回缓存值、默认值、简化响应）应由**调用方**根据自身业务语义做出，而不是由被调方或中间层静默返回一个"看起来成功"的假结果。

## 动机

- 被调方不知道调用方的业务容忍度：同样的 `get_user_profile` 失败，推荐系统可以降级返回空，支付系统却不可以。
- 中间层静默降级会让问题不可观测：日志没有错误，监控没有红线，但业务已经悄悄变差。
- 降级策略与重试策略是两个正交决策：重试解决"暂时不可用"，降级解决"容忍不可用"。混在一起会让 `match` 分支既处理重试又处理降级，逻辑纠缠。

## Rust 示例

```rust
// compile with: rustc degradation-strategy-at-caller-not-callee.rs && ./degradation-strategy-at-caller-not-callee

// --- 被调方：只负责报告结果，不做降级 ---

#[derive(Debug)]
enum ProfileError {
    ServiceUnavailable,
    NotFound,
    Timeout,
}

#[derive(Debug)]
struct UserProfile {
    name: String,
    email: String,
}

/// 模拟 profile 服务，可能失败
fn fetch_profile(user_id: &str) -> Result<UserProfile, ProfileError> {
    if user_id == "timeout" {
        Err(ProfileError::Timeout)
    } else if user_id == "missing" {
        Err(ProfileError::NotFound)
    } else {
        Ok(UserProfile {
            name: format!("User-{}", user_id),
            email: format!("{}@example.com", user_id),
        })
    }
}

// --- 调用方 A：推荐系统，可以降级 ---

struct RecommendationService;

impl RecommendationService {
    fn get_profile_with_fallback(&self, user_id: &str) -> String {
        match fetch_profile(user_id) {
            Ok(profile) => profile.name,
            Err(ProfileError::NotFound) => "anonymous".to_string(),
            Err(ProfileError::ServiceUnavailable | ProfileError::Timeout) => {
                // 推荐系统容忍 profile 不可用：降级为匿名
                eprintln!("[WARN] profile service unavailable for {}, degrading", user_id);
                "anonymous".to_string()
            }
        }
    }
}

// --- 调用方 B：支付系统，不能降级 ---

struct PaymentService;

impl PaymentService {
    fn get_profile_or_reject(&self, user_id: &str) -> Result<UserProfile, String> {
        fetch_profile(user_id).map_err(|e| {
            // 支付系统不能降级：必须把错误向上传播
            format!("cannot proceed with payment for {}: {:?}", user_id, e)
        })
    }
}

fn main() {
    let rec = RecommendationService;
    let pay = PaymentService;

    // 推荐系统：降级成功
    assert_eq!(rec.get_profile_with_fallback("timeout"), "anonymous");
    println!("ok: recommendation degraded to anonymous for timeout");

    // 支付系统：拒绝降级
    let result = pay.get_profile_or_reject("timeout");
    assert!(result.is_err());
    println!("ok: payment rejected for timeout: {}", result.unwrap_err());

    // 推荐系统：正常
    assert_eq!(rec.get_profile_with_fallback("123"), "User-123");
    println!("ok: recommendation got profile for 123");

    println!("all checks passed");
}
```

## 不应该这样做

```rust ignore
// ❌ 反面模式：被调方静默降级
fn fetch_profile_with_silent_fallback(user_id: &str) -> UserProfile {
    match fetch_profile(user_id) {
        Ok(p) => p,
        Err(_) => {
            // 被调方不知道调用方是否容忍"匿名"
            // 所有调用方都被迫接受这个降级
            UserProfile {
                name: "anonymous".into(),
                email: String::new(),
            }
        }
    }
}
```

问题：
- 调用方无法区分"真实数据"和"降级数据"。
- 支付系统拿到的也是 `anonymous`，但它本应拒绝交易。
- 监控无法区分"成功"和"降级成功"。

## Go 对照

| 方面 | Rust | Go |
|------|------|----|
| 降级决策位置 | 调用方 `match` 分支 | 调用方 `if err != nil` 分支 |
| 错误传播 | `Err(e)` 向上传播 | `return err` 向上传播 |
| 降级日志 | `eprintln!` | `log.Warn` / `slog.Warn` |
| 不可降级路径 | `Result::Err` 继续传播 | `return fmt.Errorf(...)` 继续传播 |

Go 中的等价原则：`getUserProfile` 只返回 `(Profile, error)`，调用方决定是 `return profile, nil`（降级为默认）还是 `return Profile{}, err`（继续传播）。中间层不要 `return defaultProfile, nil`。

## 复盘问题

1. 你的降级决策是在 service 层（调用方）还是在 repository/client 层（被调方）做的？
2. 降级返回的默认值是否被调用方误认为真实数据？
3. 降级事件是否有日志或 metric，还是静默发生？
4. 同一个被调方的两个调用方，对失败的容忍度是否相同？
