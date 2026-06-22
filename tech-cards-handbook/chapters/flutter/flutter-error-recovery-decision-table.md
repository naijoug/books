# Flutter 错误恢复路径需要一张决策表串起来

## 问题

Flutter 页面通常同时处理 repository 失败、重试、缓存降级、表单字段错误、SnackBar 文案和路由跳转。如果这些判断散落在 widget、ViewModel、repository adapter 和按钮回调里，review 时很难确认：某个错误到底应该自动重试、展示字段错误、回退到缓存、要求重新登录，还是上报为不可恢复故障。

## 要点

- 先把底层异常翻译成稳定的领域错误码，再让 UI / ViewModel 根据错误码查恢复决策。
- 决策表至少包含 `action`、`retryable`、`degraded`、`message` 和可选的 `fieldName` / `route`，不要只返回一段用户文案。
- widget 只渲染决策结果：显示字段错误、启用重试按钮、使用缓存态或导航登录页；不要在 `build` 或 `onPressed` 里重新分类底层异常。
- 对于移动端生命周期，决策结果写入状态前仍要检查 `mounted`、请求 token 或 ViewModel 是否已 dispose。

| 维度 | 零散判断 | 决策表 |
|---|---|---|
| 错误来源 | widget 读取 HTTP / SDK / storage 文案 | adapter 输出领域错误码 |
| 恢复动作 | `catch` 里临时 show toast / retry | `RecoveryAction` 穷尽表达 |
| UI 状态 | 字段错误、缓存态和重试按钮互相覆盖 | 决策结果驱动单一 ViewModel state |
| 审查方式 | 需要读完整页面流程 | 一张表能发现遗漏错误码 |

## 示例

```dart
// flutter-error-recovery-decision-table.dart
enum ProfileErrorCode {
  userNotFound,
  emailAlreadyUsed,
  serviceUnavailable,
  unauthenticated,
  internalError,
}

enum RecoveryAction {
  showFieldError,
  retry,
  useCachedProfile,
  requireLogin,
  showSafeError,
}

class RecoveryDecision {
  const RecoveryDecision({
    required this.action,
    required this.message,
    required this.retryable,
    required this.degraded,
    this.fieldName,
    this.route,
  });

  final RecoveryAction action;
  final String message;
  final bool retryable;
  final bool degraded;
  final String? fieldName;
  final String? route;
}

const recoveryTable = <ProfileErrorCode, RecoveryDecision>{
  ProfileErrorCode.userNotFound: RecoveryDecision(
    action: RecoveryAction.useCachedProfile,
    message: '暂时显示本地资料',
    retryable: false,
    degraded: true,
  ),
  ProfileErrorCode.emailAlreadyUsed: RecoveryDecision(
    action: RecoveryAction.showFieldError,
    message: '邮箱已被占用',
    retryable: false,
    degraded: false,
    fieldName: 'email',
  ),
  ProfileErrorCode.serviceUnavailable: RecoveryDecision(
    action: RecoveryAction.retry,
    message: '服务暂时不可用，请稍后重试',
    retryable: true,
    degraded: false,
  ),
  ProfileErrorCode.unauthenticated: RecoveryDecision(
    action: RecoveryAction.requireLogin,
    message: '请重新登录',
    retryable: false,
    degraded: false,
    route: '/login',
  ),
  ProfileErrorCode.internalError: RecoveryDecision(
    action: RecoveryAction.showSafeError,
    message: '操作失败，请稍后再试',
    retryable: false,
    degraded: false,
  ),
};

sealed class ProfileError implements Exception {
  const ProfileError(this.code, {this.cause});

  final ProfileErrorCode code;
  final Object? cause;
}

final class ProfileFailure extends ProfileError {
  const ProfileFailure(super.code, {super.cause});
}

RecoveryDecision decideProfileRecovery(ProfileError error) {
  return recoveryTable[error.code] ?? recoveryTable[ProfileErrorCode.internalError]!;
}

class ProfileViewState {
  const ProfileViewState({
    required this.message,
    required this.canRetry,
    required this.degraded,
    this.fieldErrors = const {},
    this.redirectTo,
  });

  final String message;
  final bool canRetry;
  final bool degraded;
  final Map<String, String> fieldErrors;
  final String? redirectTo;
}

ProfileViewState toViewState(ProfileError error) {
  final decision = decideProfileRecovery(error);

  return switch (decision.action) {
    RecoveryAction.showFieldError => ProfileViewState(
        message: '请修改表单后重试',
        canRetry: false,
        degraded: false,
        fieldErrors: {decision.fieldName!: decision.message},
      ),
    RecoveryAction.retry => ProfileViewState(
        message: decision.message,
        canRetry: true,
        degraded: false,
      ),
    RecoveryAction.useCachedProfile => ProfileViewState(
        message: decision.message,
        canRetry: false,
        degraded: true,
      ),
    RecoveryAction.requireLogin => ProfileViewState(
        message: decision.message,
        canRetry: false,
        degraded: false,
        redirectTo: decision.route,
      ),
    RecoveryAction.showSafeError => ProfileViewState(
        message: decision.message,
        canRetry: false,
        degraded: false,
      ),
  };
}

void main() {
  final email = toViewState(
    const ProfileFailure(ProfileErrorCode.emailAlreadyUsed),
  );
  assert(email.fieldErrors['email'] == '邮箱已被占用');
  assert(!email.canRetry);

  final temporary = toViewState(
    const ProfileFailure(
      ProfileErrorCode.serviceUnavailable,
      cause: 'DioException host=10.0.0.12 trace=abc',
    ),
  );
  assert(temporary.canRetry);
  assert(!temporary.message.contains('10.0.0.12'));
  assert(!temporary.message.contains('trace=abc'));

  final missing = toViewState(
    const ProfileFailure(ProfileErrorCode.userNotFound),
  );
  assert(missing.degraded);

  final auth = toViewState(
    const ProfileFailure(ProfileErrorCode.unauthenticated),
  );
  assert(auth.redirectTo == '/login');
}
```

在真实页面中，`toViewState` 的结果可以进入 `ChangeNotifier`、`ValueNotifier`、Riverpod provider 或 Bloc state；widget 只负责根据 `canRetry`、`fieldErrors`、`degraded` 和 `redirectTo` 渲染，不再重新解释底层错误。

## 坑

- **只维护错误码，不维护动作表**：新增 `ProfileErrorCode` 后没有补决策，UI 默认进入笼统错误态，用户不知道能否恢复。
- **把降级藏在 repository**：repository 返回假资料，UI 看不到 `degraded` 标记，后续会把缓存当成真实数据继续提交。
- **字段错误和重试按钮同时出现**：`emailAlreadyUsed` 需要用户修改输入，不应该展示“重试”按钮制造无效请求。
- **决策表输出底层异常**：`cause` 只能进入日志或 tracing，用户可见 `message` 必须来自安全字段。
- **异步结果越过生命周期**：即使决策正确，页面 dispose 或请求 token 过期后也不能把旧决策写回 UI。

## 检查

- 每个领域错误码是否都能在一张表里看到恢复动作、用户文案、是否可重试和是否降级？
- widget / ViewModel 是否只消费 `RecoveryDecision` 或派生 ViewState，而不是读取 HTTP status、SQL state、SDK error string？
- 字段错误、重试、登录跳转、缓存降级和安全错误是否互斥，避免同一个失败显示多个恢复入口？
- 降级态是否有显式 `degraded` 标记，并在 UI、日志或埋点中可观察？
- 与 [`flutter-external-error-codes-domain-defined-not-leaked.md`](flutter-external-error-codes-domain-defined-not-leaked.md) 和 [`flutter-retry-policy-explicit-not-hidden-loop.md`](flutter-retry-policy-explicit-not-hidden-loop.md) 一起检查：领域错误码、重试策略和 UI 恢复动作是否指向同一套决策。
- 对照 Rust 的 [`../rust/error-recovery-path-needs-one-decision-table.md`](../rust/error-recovery-path-needs-one-decision-table.md)、TypeScript 的 [`../typescript/error-recovery-path-needs-one-decision-table.md`](../typescript/error-recovery-path-needs-one-decision-table.md) 和 Python 的 [`../python/error-recovery-path-needs-one-decision-table.md`](../python/error-recovery-path-needs-one-decision-table.md)，确认前后端恢复动作命名一致。
