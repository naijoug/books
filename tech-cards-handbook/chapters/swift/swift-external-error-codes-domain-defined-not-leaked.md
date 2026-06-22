# 对外错误码要由领域定义，不要泄漏底层错误

**问题**：Swift App 调用网络、数据库或系统 API 失败时，UI 往往会直接展示 `localizedDescription`，或者把 `URLError.Code`、HTTP status、SQLite code 传到 ViewModel。这样做会让用户看到不稳定的底层文案，也会让重试、登录跳转和降级策略依赖某个 SDK 的错误细节。

**要点**：

- 在 repository / service adapter 边界把底层错误翻译成领域错误，不要让 ViewModel 认识 `URLError`、数据库错误或第三方 SDK 类型。
- 对外错误码使用稳定的 enum，例如 `ProfileErrorCode`；UI 文案、埋点和恢复动作都围绕这个 enum 决策。
- 诊断上下文要进日志或关联值；用户可见消息只暴露安全、可本地化的 `safeMessage`。
- 先有领域错误码，再接 [`swift-retry-policy-explicit-not-hidden-loop.md`](swift-retry-policy-explicit-not-hidden-loop.md) 里的显式重试策略；否则重试条件会退化成字符串匹配。

| 边界 | 不推荐 | 推荐 |
|---|---|---|
| Repository 返回 | `throw error` | `throw ProfileError.storageUnavailable` |
| ViewModel 判断 | `if error is URLError` | `switch error.code` |
| 用户文案 | `error.localizedDescription` | `error.safeMessage` |
| 诊断信息 | 拼进 toast | 进入 logger / telemetry |

**示例**：

```swift
import Foundation

enum StorageFailure: Error {
    case rowNotFound(table: String, id: String)
    case uniqueViolation(index: String)
    case connectionLost(underlying: Error)
}

enum ProfileErrorCode: String {
    case profileNotFound
    case duplicateEmail
    case storageUnavailable
    case unknown
}

struct ProfileError: Error {
    let code: ProfileErrorCode
    let safeMessage: String
    let diagnostic: String
}

func translateStorageFailure(_ error: Error) -> ProfileError {
    switch error {
    case let failure as StorageFailure:
        switch failure {
        case let .rowNotFound(table, id):
            return ProfileError(
                code: .profileNotFound,
                safeMessage: "Profile was not found.",
                diagnostic: "missing row table=\(table) id=\(id)"
            )
        case let .uniqueViolation(index):
            return ProfileError(
                code: .duplicateEmail,
                safeMessage: "This email is already used.",
                diagnostic: "unique violation index=\(index)"
            )
        case let .connectionLost(underlying):
            return ProfileError(
                code: .storageUnavailable,
                safeMessage: "Profile service is temporarily unavailable.",
                diagnostic: "storage connection lost: \(underlying)"
            )
        }
    default:
        return ProfileError(
            code: .unknown,
            safeMessage: "Something went wrong.",
            diagnostic: "unexpected error: \(error)"
        )
    }
}

func viewMessage(for error: ProfileError) -> String {
    switch error.code {
    case .profileNotFound, .duplicateEmail, .storageUnavailable, .unknown:
        return error.safeMessage
    }
}
```

**坑**：

- 在 SwiftUI `View` 或 ViewModel 里直接 `catch let error as URLError`，导致 UI 层依赖网络库或存储实现。
- 把 `localizedDescription` 当作错误码；系统语言、SDK 版本或第三方库升级都会改变文案。
- 为了“保留根因”把 SQL、文件路径、token 或第三方响应体直接展示给用户。
- 领域错误码只覆盖 happy path，未知错误没有统一 `.unknown` / `.storageUnavailable` 分支，导致调用方继续回退到底层错误。

**检查**：

- Repository / adapter 是否把底层 `Error` 翻译成领域 `Error`，而不是把 SDK 类型传到 UI？
- 对外错误码是否是稳定 enum，并能被文案、本地化、埋点和恢复动作复用？
- 用户可见消息是否来自 `safeMessage` 或本地化 key，而不是 `localizedDescription`？
- 诊断上下文是否仍被保留在日志/关联值中，便于排查但不会泄漏给用户？
- 重试和降级策略是否基于领域错误码，而不是底层错误字符串？

对照阅读：[`../flutter/flutter-external-error-codes-domain-defined-not-leaked.md`](../flutter/flutter-external-error-codes-domain-defined-not-leaked.md)、[`../typescript/external-error-codes-domain-defined-not-leaked.md`](../typescript/external-error-codes-domain-defined-not-leaked.md)、[`../python/external-error-codes-domain-defined-not-leaked.md`](../python/external-error-codes-domain-defined-not-leaked.md)、[`../go/external-error-codes-domain-defined-not-leaked.md`](../go/external-error-codes-domain-defined-not-leaked.md)。
