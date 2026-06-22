# Swift 错误恢复路径需要一张决策表串起来

**问题**：SwiftUI / UIKit 应用的错误处理常分散在 repository、ViewModel、`catch` 分支、alert 文案和按钮重试回调里。每段代码都可能“看起来合理”，但 review 时很难确认：某个领域错误到底应该展示字段错误、允许重试、使用缓存降级、跳转登录，还是只显示安全错误。

**要点**：

- 先把底层错误翻译成稳定的领域错误码，再用一张 `RecoveryDecision` 表决定 UI / 调用方动作。
- 决策表至少表达 `action`、`retryable`、`degraded`、`message`，以及可选的字段名或路由；不要只返回一段 alert 文案。
- ViewModel 只消费决策结果并生成 `ViewState`，不要在每个 `catch` 里重新判断 `URLError`、SQLite code 或 SDK message。
- 降级必须显式暴露 `degraded` 标记，避免调用方把缓存或默认值当成真实数据继续提交。

| 维度 | 零散 `catch` | 决策表 |
|---|---|---|
| 错误分类 | ViewModel 读取底层 `Error` | adapter 输出 `ProfileErrorCode` |
| 恢复动作 | alert、retry、fallback 分散实现 | `RecoveryAction` 穷尽表达 |
| UI 状态 | 文案、按钮和缓存态互相覆盖 | `ProfileViewState` 由决策派生 |
| 审查方式 | 需要读完整页面和调用链 | 一张表能发现遗漏错误码 |

**示例**：

```swift
import Foundation

enum ProfileErrorCode: String, CaseIterable {
    case profileNotFound
    case duplicateEmail
    case storageUnavailable
    case unauthenticated
    case unknown
}

struct ProfileError: Error {
    let code: ProfileErrorCode
    let safeMessage: String
    let diagnostic: String
}

enum RecoveryAction: String {
    case showFieldError
    case retry
    case useCachedProfile
    case requireLogin
    case showSafeError
}

struct RecoveryDecision {
    let action: RecoveryAction
    let message: String
    let retryable: Bool
    let degraded: Bool
    let fieldName: String?
    let route: String?
}

let recoveryTable: [ProfileErrorCode: RecoveryDecision] = [
    .profileNotFound: RecoveryDecision(
        action: .useCachedProfile,
        message: "暂时显示本地资料",
        retryable: false,
        degraded: true,
        fieldName: nil,
        route: nil
    ),
    .duplicateEmail: RecoveryDecision(
        action: .showFieldError,
        message: "邮箱已被占用",
        retryable: false,
        degraded: false,
        fieldName: "email",
        route: nil
    ),
    .storageUnavailable: RecoveryDecision(
        action: .retry,
        message: "服务暂时不可用，请稍后重试",
        retryable: true,
        degraded: false,
        fieldName: nil,
        route: nil
    ),
    .unauthenticated: RecoveryDecision(
        action: .requireLogin,
        message: "请重新登录",
        retryable: false,
        degraded: false,
        fieldName: nil,
        route: "/login"
    ),
    .unknown: RecoveryDecision(
        action: .showSafeError,
        message: "操作失败，请稍后再试",
        retryable: false,
        degraded: false,
        fieldName: nil,
        route: nil
    ),
]

func decideRecovery(for error: ProfileError) -> RecoveryDecision {
    recoveryTable[error.code] ?? recoveryTable[.unknown]!
}

struct ProfileViewState {
    let message: String
    let canRetry: Bool
    let degraded: Bool
    let fieldErrors: [String: String]
    let redirectTo: String?
}

func toViewState(_ error: ProfileError) -> ProfileViewState {
    let decision = decideRecovery(for: error)

    switch decision.action {
    case .showFieldError:
        return ProfileViewState(
            message: "请修改表单后重试",
            canRetry: false,
            degraded: false,
            fieldErrors: [decision.fieldName!: decision.message],
            redirectTo: nil
        )
    case .retry:
        return ProfileViewState(
            message: decision.message,
            canRetry: true,
            degraded: false,
            fieldErrors: [:],
            redirectTo: nil
        )
    case .useCachedProfile:
        return ProfileViewState(
            message: decision.message,
            canRetry: false,
            degraded: true,
            fieldErrors: [:],
            redirectTo: nil
        )
    case .requireLogin:
        return ProfileViewState(
            message: decision.message,
            canRetry: false,
            degraded: false,
            fieldErrors: [:],
            redirectTo: decision.route
        )
    case .showSafeError:
        return ProfileViewState(
            message: decision.message,
            canRetry: false,
            degraded: false,
            fieldErrors: [:],
            redirectTo: nil
        )
    }
}

let duplicate = ProfileError(
    code: .duplicateEmail,
    safeMessage: "This email is already used.",
    diagnostic: "unique index users_email_key"
)
let fieldState = toViewState(duplicate)
assert(fieldState.fieldErrors["email"] == "邮箱已被占用")
assert(!fieldState.canRetry)

let temporary = ProfileError(
    code: .storageUnavailable,
    safeMessage: "Profile service is temporarily unavailable.",
    diagnostic: "host=10.0.0.8 trace=abc"
)
let retryState = toViewState(temporary)
assert(retryState.canRetry)
assert(!retryState.message.contains("10.0.0.8"))
assert(!retryState.message.contains("trace=abc"))

let missing = ProfileError(
    code: .profileNotFound,
    safeMessage: "Profile was not found.",
    diagnostic: "row id=42 missing"
)
assert(toViewState(missing).degraded)

let unauthenticated = ProfileError(
    code: .unauthenticated,
    safeMessage: "Please sign in again.",
    diagnostic: "token expired"
)
assert(toViewState(unauthenticated).redirectTo == "/login")

assert(
    Set(recoveryTable.keys) == Set(ProfileErrorCode.allCases),
    "每个领域错误码都必须有恢复决策"
)
```

真实项目里，`toViewState` 的结果可以进入 `@Published` state、Reducer state 或 UIKit presenter；View / ViewController 只根据 `canRetry`、`fieldErrors`、`degraded` 和 `redirectTo` 渲染，不再解释底层错误。

**坑**：

- 只新增 `ProfileErrorCode`，没有补 `recoveryTable`；Swift 不会自动要求字典覆盖所有 enum case，需要用测试或断言守住覆盖率。
- ViewModel 直接展示 `localizedDescription`，把 host、SQL、token、SDK message 暴露给用户。
- repository 静默返回缓存对象，UI 没有 `degraded` 标记，后续会把旧数据当作真实结果继续提交。
- 字段错误和重试按钮同时出现：`duplicateEmail` 需要用户修改输入，不应该再自动重试同一请求。
- 决策正确但异步结果越过生命周期：SwiftUI task 取消或 UIKit view disappeared 后，不应把旧决策写回界面。

**检查**：

- 每个领域错误码是否都能在一张表里看到恢复动作、用户文案、是否可重试和是否降级？
- ViewModel / Presenter 是否只消费 `RecoveryDecision` 或派生 ViewState，而不是读取 `URLError`、数据库错误码或 SDK 字符串？
- 字段错误、重试、登录跳转、缓存降级和安全错误是否互斥，避免同一个失败显示多个恢复入口？
- 降级态是否有显式 `degraded` 标记，并在 UI、日志或埋点中可观察？
- 与 [`swift-external-error-codes-domain-defined-not-leaked.md`](swift-external-error-codes-domain-defined-not-leaked.md) 和 [`swift-retry-policy-explicit-not-hidden-loop.md`](swift-retry-policy-explicit-not-hidden-loop.md) 一起检查：领域错误码、重试策略和 UI 恢复动作是否指向同一套决策。
- 对照 Flutter 的 [`../flutter/flutter-error-recovery-decision-table.md`](../flutter/flutter-error-recovery-decision-table.md)、TypeScript 的 [`../typescript/error-recovery-path-needs-one-decision-table.md`](../typescript/error-recovery-path-needs-one-decision-table.md) 和 Python 的 [`../python/error-recovery-path-needs-one-decision-table.md`](../python/error-recovery-path-needs-one-decision-table.md)，确认移动端和后端恢复动作命名一致。
