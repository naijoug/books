# 错误恢复要用显式重试策略，而不是在错误处理里循环

## 核心要点

错误处理决定"出了什么错"，重试策略决定"还要不要再来一次"。两者应该分开：

- 错误处理：用 `Result` / `match` 分类错误，决定哪些可重试、哪些应立即失败。
- 重试策略：在调用方用显式的最大次数、退避间隔和可重试错误集合控制循环。
- 不要在 `match err` 分支里直接 `continue` 或递归调用自己——重试逻辑会散落在错误处理的每个分支里，难以测试、难以观测。

## Rust 示例

```rust
// retry-strategy-explicit.rs
use std::thread;
use std::time::Duration;

/// 可重试错误 vs 致命错误
enum FetchError {
    Timeout,
    RateLimited,
    NotFound,
    Unauthorized,
}

impl std::fmt::Display for FetchError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            FetchError::Timeout => write!(f, "timeout"),
            FetchError::RateLimited => write!(f, "rate limited"),
            FetchError::NotFound => write!(f, "not found"),
            FetchError::Unauthorized => write!(f, "unauthorized"),
        }
    }
}

/// 模拟一个可能失败的操作
fn fetch_resource(id: u32, attempt: u32) -> Result<String, FetchError> {
    if id == 0 {
        return Err(FetchError::NotFound);
    }
    if attempt < 2 {
        return Err(FetchError::Timeout);
    }
    Ok(format!("resource-{}", id))
}

/// 错误分类：哪些值得重试
fn is_retryable(err: &FetchError) -> bool {
    matches!(err, FetchError::Timeout | FetchError::RateLimited)
}

/// 显式重试策略：最大次数 + 固定退避
struct RetryPolicy {
    max_attempts: u32,
    backoff_ms: u64,
}

impl RetryPolicy {
    fn new(max_attempts: u32, backoff_ms: u64) -> Self {
        Self { max_attempts, backoff_ms }
    }

    // 实际项目中 execute 接受一个 is_retryable 判断函数作为参数
    // 此处省略泛型实现，见下方 fetch_with_retry 的完整版
}

/// 完整版：重试策略 + 错误分类分离
fn fetch_with_retry(id: u32, policy: &RetryPolicy) -> Result<String, FetchError> {
    let mut attempt = 0;
    loop {
        attempt += 1;
        match fetch_resource(id, attempt) {
            Ok(value) => return Ok(value),
            Err(err) if !is_retryable(&err) => {
                // 不可重试的错误，立即返回
                return Err(err);
            }
            Err(err) if attempt >= policy.max_attempts => {
                // 重试次数用尽
                eprintln!(
                    "attempt {}/{} failed: {} — giving up",
                    attempt, policy.max_attempts, err
                );
                return Err(err);
            }
            Err(err) => {
                // 可重试，等一下再来
                eprintln!(
                    "attempt {}/{} failed: {} — retrying in {}ms",
                    attempt, policy.max_attempts, err, policy.backoff_ms
                );
                thread::sleep(Duration::from_millis(policy.backoff_ms));
            }
        }
    }
}

fn main() {
    // 不可重试：NotFound 直接返回
    match fetch_with_retry(0, &RetryPolicy::new(3, 100)) {
        Ok(v) => println!("got: {}", v),
        Err(e) => println!("final error: {}", e),
    }

    // 可重试：前两次 Timeout，第三次成功
    match fetch_with_retry(1, &RetryPolicy::new(3, 10)) {
        Ok(v) => println!("got: {}", v),
        Err(e) => println!("final error: {}", e),
    }

    // 重试次数不够：两次就放弃
    match fetch_with_retry(1, &RetryPolicy::new(1, 10)) {
        Ok(v) => println!("got: {}", v),
        Err(e) => println!("final error: {}", e),
    }
}
```

## 运行方式

```bash
rustc retry-strategy-explicit-not-implicit-loop.rs -o retry-demo && ./retry-demo
# expected output:
# final error: not found
# attempt 1/3 failed: timeout — retrying in 10ms
# got: resource-1
# attempt 1/1 failed: timeout — giving up
# final error: timeout
```

## 反面模式

```rust,no_run
// ❌ 重试逻辑散落在错误处理分支里
fn fetch_with_inline_retry(id: u32) -> Result<String, FetchError> {
    match fetch_resource(id, 1) {
        Ok(v) => Ok(v),
        Err(FetchError::Timeout) => {
            // 隐式重试 #1
            match fetch_resource(id, 2) {
                Ok(v) => Ok(v),
                Err(FetchError::Timeout) => {
                    // 隐式重试 #2
                    match fetch_resource(id, 3) {
                        Ok(v) => Ok(v),
                        Err(e) => Err(e),
                    }
                }
                Err(e) => Err(e),
            }
        }
        Err(e) => Err(e),
    }
}
```

问题：
- 最大重试次数嵌套在 match 深度里，不显眼。
- 没有退避间隔，容易把下游打爆。
- 新增一种可重试错误需要改每一层嵌套。
- 无法在测试中替换重试策略。

## 跨语言对照

| 关注点 | Rust | Go |
|--------|------|----|
| 错误分类 | `match` / `is_retryable(&err)` | `errors.Is` / `errors.As` |
| 重试策略 | `RetryPolicy` struct + `loop` | `for attempt := 1; attempt <= max; attempt++` |
| 退避 | `thread::sleep(Duration)` | `time.Sleep(duration)` |
| 可重试集合 | `matches!(err, Timeout \| RateLimited)` | `errors.Is(err, ErrTimeout) \|\| errors.Is(err, ErrRateLimited)` |
| 不可重试退出 | `Err(err) if !is_retryable(&err)` | `return err` (在 for 循环外) |

Go 对照提示：Go 的 `errors.Is` / `errors.As` 和显式 `for` 循环重试模式与 Rust 的 `match` + `loop` 结构上是同一思路——错误分类和重试策略应分离。

## 自检问题

1. 你的重试最大次数和退避间隔是硬编码在 match/for 里，还是在一个可配置的策略对象里？
2. 新增一种可重试错误时，需要改几处代码？
3. 测试重试耗尽路径时，能不依赖真实 sleep 吗？
4. 监控面板能看到每次重试的计数和最终失败原因吗？
