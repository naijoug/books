# Swift 降级策略应由调用方决定，不要藏在 repository 里

**问题**：Swift app 经常在 repository、SDK adapter 或 ViewModel 的 `catch` 里顺手返回空数组、默认资料或本地缓存。这样 UI 看起来“没崩”，但上层再也分不清：这次是真没有数据、依赖失败后被缓存兜底，还是用户必须重新登录。降级策略一旦藏在被调方里，支付、风控、资料页和推荐卡片会被迫共享同一种假成功。

**要点**：

- Repository / client 只报告事实：成功返回领域对象，失败抛出可分类领域错误；不要替所有调用方选择默认值。
- 调用方按业务场景决定是否降级：推荐卡片可以显示缓存资料，支付验证必须中断，资料编辑可能要求重新登录。
- 降级结果必须显式携带 `degraded`、`source` 或埋点字段，不能把缓存值伪装成新鲜值。
- 不可降级路径继续保留底层诊断上下文，供日志、trace 和上层错误恢复决策使用。

| 场景 | 被调方隐藏降级 | 调用方显式降级 |
|---|---|---|
| 推荐卡片 | repository 返回匿名用户 | ViewModel 决定用缓存并标记 `degraded` |
| 支付/风控 | 误把缓存资料当真实资料 | 调用方传播错误并阻断流程 |
| 资料编辑 | SDK message 直接进 alert | 领域错误码进入恢复决策表 |
| 观测 | 看不到默认值来源 | metric / log 标记降级原因 |

**示例**：

```swift
import Foundation

enum ProfileErrorCode: String {
    case notFound
    case serviceUnavailable
    case unauthenticated
}

struct ProfileError: Error {
    let code: ProfileErrorCode
    let diagnostic: String
}

struct Profile {
    let userId: String
    let displayName: String
    let verified: Bool
}

struct ProfileSnapshot: Equatable {
    let displayName: String
    let degraded: Bool
    let source: String
}

final class ProfileRepository {
    func fetch(userId: String) throws -> Profile {
        // Repository 只报告事实；不要在这里返回 Profile(userId: userId, displayName: "anonymous", verified: false)。
        switch userId {
        case "missing":
            throw ProfileError(code: .notFound, diagnostic: "row missing for \(userId)")
        case "timeout":
            throw ProfileError(code: .serviceUnavailable, diagnostic: "profile api timeout")
        case "expired":
            throw ProfileError(code: .unauthenticated, diagnostic: "token expired")
        default:
            return Profile(userId: userId, displayName: "Ada", verified: true)
        }
    }
}

struct ProfileCache {
    var snapshots: [String: ProfileSnapshot] = [:]

    func snapshot(for userId: String) -> ProfileSnapshot? {
        snapshots[userId]
    }
}

struct RecommendationPresenter {
    let repository: ProfileRepository
    let cache: ProfileCache

    func cardSnapshot(userId: String) throws -> ProfileSnapshot {
        do {
            let profile = try repository.fetch(userId: userId)
            return ProfileSnapshot(
                displayName: profile.displayName,
                degraded: false,
                source: "remote"
            )
        } catch let error as ProfileError where error.code == .notFound {
            return ProfileSnapshot(displayName: "anonymous", degraded: true, source: "empty-fallback")
        } catch let error as ProfileError where error.code == .serviceUnavailable {
            if let cached = cache.snapshot(for: userId) {
                return ProfileSnapshot(displayName: cached.displayName, degraded: true, source: "cache")
            }
            throw ProfileError(code: error.code, diagnostic: "recommendation card unavailable: \(error.diagnostic)")
        }
    }
}

struct PaymentRiskService {
    let repository: ProfileRepository

    func verifiedProfile(userId: String) throws -> Profile {
        do {
            let profile = try repository.fetch(userId: userId)
            guard profile.verified else {
                throw ProfileError(code: .notFound, diagnostic: "profile is not verified")
            }
            return profile
        } catch let error as ProfileError {
            // 支付风控不能用缓存或匿名用户继续；保留上下文并中断。
            throw ProfileError(code: error.code, diagnostic: "cannot verify payer \(userId): \(error.diagnostic)")
        }
    }
}

let repository = ProfileRepository()
let cache = ProfileCache(snapshots: [
    "timeout": ProfileSnapshot(displayName: "Cached Ada", degraded: true, source: "cache")
])
let recommendation = RecommendationPresenter(repository: repository, cache: cache)
let payment = PaymentRiskService(repository: repository)

let ok = try recommendation.cardSnapshot(userId: "u-1")
assert(ok == ProfileSnapshot(displayName: "Ada", degraded: false, source: "remote"))

let missing = try recommendation.cardSnapshot(userId: "missing")
assert(missing == ProfileSnapshot(displayName: "anonymous", degraded: true, source: "empty-fallback"))

let cached = try recommendation.cardSnapshot(userId: "timeout")
assert(cached == ProfileSnapshot(displayName: "Cached Ada", degraded: true, source: "cache"))

do {
    _ = try payment.verifiedProfile(userId: "missing")
    assertionFailure("payment risk must not use anonymous fallback")
} catch let error as ProfileError {
    assert(error.code == .notFound)
    assert(error.diagnostic.contains("cannot verify payer"))
}
```

真实项目里，`RecommendationPresenter` 可以是 SwiftUI ViewModel、Reducer 或 UIKit Presenter；关键不是名字，而是让“能否降级”跟业务入口绑定，而不是被 repository 的默认返回值提前决定。

**坑**：

- Repository 遇到 404 / timeout / decode error 都返回空 `Profile`，导致调用方误以为远端真实返回空资料。
- 所有 `ProfileError` 都在同一个 `catch` 里降级成缓存，支付、风控、写操作也被错误放行。
- 降级后没有 `degraded` 或 `source`，UI、日志和埋点都看不出当前值来自缓存或默认值。
- 不可降级时重新抛出通用错误但丢掉 `diagnostic`，上层无法定位是认证、存储还是网络问题。
- 降级策略和错误恢复决策表各写一套条件，导致同一个错误码在不同页面出现不同动作。

**检查**：

- 搜索 repository / client / SDK adapter 的 `catch`，是否返回空数组、默认对象、缓存值或安全文案来伪装成功？
- 每个调用方是否写清“可降级错误”和“必须传播错误”，并用领域错误码而不是底层 SDK message 判断？
- 降级结果是否带有 `degraded`、`source`、metric 或日志字段，方便事故复盘？
- 支付、风控、写操作、权限校验等不可降级路径是否保留诊断上下文并明确中断？
- 与 [`swift-external-error-codes-domain-defined-not-leaked.md`](swift-external-error-codes-domain-defined-not-leaked.md)、[`swift-retry-policy-explicit-not-hidden-loop.md`](swift-retry-policy-explicit-not-hidden-loop.md) 和 [`swift-error-recovery-decision-table.md`](swift-error-recovery-decision-table.md) 一起检查：领域错误码、重试、降级和 UI 恢复动作是否来自同一套规则。
- 对照 Python 的 [`../python/degradation-strategy-at-caller-not-callee.md`](../python/degradation-strategy-at-caller-not-callee.md)、Go 的 [`../go/degradation-strategy-at-caller-not-callee.md`](../go/degradation-strategy-at-caller-not-callee.md)、Rust 的 [`../rust/degradation-strategy-at-caller-not-callee.md`](../rust/degradation-strategy-at-caller-not-callee.md) 和 TypeScript 的 [`../typescript/degradation-strategy-at-caller-not-callee.md`](../typescript/degradation-strategy-at-caller-not-callee.md)，确认前后端对“降级由调用方决定”的边界一致。
