# 重试策略要显式化，而不是藏在循环和 guard 里

**问题**：调用网络请求、文件读取或数据库操作失败时，什么时候该重试？如果把 `while true` 和 `try?` 直接写在错误处理分支里，后续很容易看不清哪些错误可重试、最多试几次、退避多久，以及耗尽后返回什么。

**要点**：

- 先把错误分成可重试、不可重试和调用方需要处理的领域错误；不要靠字符串匹配底层错误描述。
- 用 `RetryPolicy` 之类的小结构体表达最大尝试次数和退避间隔，让策略能被测试、配置和复用。
- 重试函数只负责"按策略重新调用一次操作"；业务函数仍然负责把底层错误转换成领域错误。
- 重试耗尽后要返回最后一次失败，并用关联值保留错误链；日志或上层 caller 才能看到根因。

| 维度 | 隐式循环 | 显式策略 |
|---|---|---|
| 可重试条件 | 散落在 `catch` 分支里 | `isRetryable(_:)` 单独定义 |
| 次数和退避 | 魔法数字写在函数体 | `RetryPolicy(maxAttempts:backoff:)` |
| 测试方式 | 只能跑完整业务流程 | 可注入假操作和零退避 |
| 耗尽语义 | 经常只返回原始 `Error` | 包装为 `RetryExhausted` 关联值 |

**示例**：

```swift
import Foundation

enum AppError: Error {
    case temporary(String)
    case forbidden
    case retryExhausted(lastError: Error, attempts: Int)
}

struct RetryPolicy {
    var maxAttempts: Int
    var backoff: TimeInterval

    init(maxAttempts: Int = 3, backoff: TimeInterval = 0.2) {
        self.maxAttempts = max(1, maxAttempts)
        self.backoff = backoff
    }
}

func isRetryable(_ error: Error) -> Bool {
    if case AppError.temporary = error { return true }
    return false
}

func withRetry<T>(
    _ policy: RetryPolicy,
    operation: () async throws -> T
) async throws -> T {
    var lastError: Error?

    for attempt in 1...policy.maxAttempts {
        do {
            return try await operation()
        } catch {
            if !isRetryable(error) {
                throw error
            }
            lastError = error
            if attempt < policy.maxAttempts, policy.backoff > 0 {
                try? await Task.sleep(nanoseconds: UInt64(policy.backoff * 1_000_000_000))
            }
        }
    }

    throw AppError.retryExhausted(
        lastError: lastError!,
        attempts: policy.maxAttempts
    )
}

// 使用示例
func fetchProfile() async throws -> String {
    var attempts = 0
    return try await withRetry(RetryPolicy(maxAttempts: 3, backoff: 0)) {
        attempts += 1
        if attempts < 3 {
            throw AppError.temporary("upstream timeout")
        }
        return "profile-data"
    }
}
```

**坑**：

- 把 `Task.sleep`、最大次数和错误判断直接塞进 ViewModel 方法，导致每个调用点都有一份不同的重试规则。
- 用 `error.localizedDescription.contains("timeout")` 判断是否重试；底层 SDK 改了错误描述，恢复策略就失效。
- 重试耗尽后返回一个全新的错误，忘记携带原始错误，调用方无法判断根因。
- 对不可重试错误（如认证失败）也继续重试，放大权限错误或幂等性问题。
- 在 Swift concurrency 中使用 `Task.sleep` 时忘记检查 `CancellationError`，导致 Task 取消后仍继续重试。

**检查**：

- 可重试错误集合是否有稳定的枚举 case 或自定义 `Error` 类型，而不是散落的字符串判断？
- 最大尝试次数、退避间隔和是否开启重试是否能在测试里设成小值或零值？
- 重试耗尽后，调用方能否从 `retryExhausted(lastError:)` 中取出最后一次失败的根因？
- Task 被取消时是否立即停止重试并抛出 `CancellationError`？
