# Flutter 对外错误码要来自领域错误

## 问题

Flutter 页面经常要把 repository、HTTP client、平台通道或第三方 SDK 的失败展示给用户。如果 UI 直接展示 `DioException`、HTTP status、SQLite constraint、Firebase error string 或平台异常 message，就会把实现细节变成产品契约：文案不稳定、难以本地化，也可能泄漏 host、表名、索引名或调试路径。

## 要点

- 在 data / adapter 边界把底层异常翻译成稳定的领域错误，例如 `ProfileError.notFound`、`ProfileError.emailTaken`、`ProfileError.serviceUnavailable`。
- UI 层只认识领域错误码和安全 message；底层异常保留在日志、crash report 或 tracing context 中。
- HTTP status 不是业务 code：`409` 只能说明冲突，真正给用户和调用方决策的是 `EMAIL_ALREADY_USED` 这类领域码。
- 错误码、用户可见文案和恢复动作要能一一对应：重试、登录、修改输入、稍后再试分别由不同 code 驱动。

## 示例

```dart
// flutter-external-error-codes-domain-defined-not-leaked.dart
enum ProfileErrorCode {
  userNotFound,
  emailAlreadyUsed,
  serviceUnavailable,
  internalError,
}

sealed class ProfileError implements Exception {
  const ProfileError(this.code, this.safeMessage, {this.cause});

  final ProfileErrorCode code;
  final String safeMessage;
  final Object? cause;
}

final class UserNotFound extends ProfileError {
  const UserNotFound(String userId, {Object? cause})
      : userId = userId,
        super(
          ProfileErrorCode.userNotFound,
          '用户不存在',
          cause: cause,
        );

  final String userId;
}

final class EmailAlreadyUsed extends ProfileError {
  const EmailAlreadyUsed({Object? cause})
      : super(
          ProfileErrorCode.emailAlreadyUsed,
          '邮箱已被占用',
          cause: cause,
        );
}

final class ProfileServiceUnavailable extends ProfileError {
  const ProfileServiceUnavailable({Object? cause})
      : super(
          ProfileErrorCode.serviceUnavailable,
          '服务暂时不可用，请稍后重试',
          cause: cause,
        );
}

final class UnknownProfileFailure extends ProfileError {
  const UnknownProfileFailure({Object? cause})
      : super(
          ProfileErrorCode.internalError,
          '操作失败，请稍后再试',
          cause: cause,
        );
}

sealed class StorageFailure {
  const StorageFailure(this.detail);
  final String detail;
}

final class RowNotFound extends StorageFailure {
  const RowNotFound(super.detail);
}

final class UniqueViolation extends StorageFailure {
  const UniqueViolation(super.detail);
}

final class PoolExhausted extends StorageFailure {
  const PoolExhausted(super.detail);
}

final class DriverFailure extends StorageFailure {
  const DriverFailure(super.detail);
}

ProfileError translateStorageFailure(StorageFailure failure, String userId) {
  return switch (failure) {
    RowNotFound() => UserNotFound(userId, cause: failure),
    UniqueViolation() => EmailAlreadyUsed(cause: failure),
    PoolExhausted() => ProfileServiceUnavailable(cause: failure),
    DriverFailure() => UnknownProfileFailure(cause: failure),
  };
}

class ProfileRepository {
  String loadName(String userId) {
    final simulatedFailures = <String, StorageFailure>{
      'missing': const RowNotFound('sql: no rows in result set'),
      'duplicate': const UniqueViolation(
        'SQLSTATE 23505 duplicate key users_email_key',
      ),
      'overloaded': const PoolExhausted('db pool exhausted at 10.0.0.12'),
      'broken': const DriverFailure('trace /srv/app/profile_repository.dart:17'),
    };

    final failure = simulatedFailures[userId];
    if (failure != null) {
      throw translateStorageFailure(failure, userId);
    }
    return 'Alice';
  }
}

class ProfileErrorView {
  const ProfileErrorView({required this.code, required this.message});

  final String code;
  final String message;
}

ProfileErrorView toViewError(Object error) {
  final profileError = error is ProfileError
      ? error
      : UnknownProfileFailure(cause: error);

  return ProfileErrorView(
    code: profileError.code.name,
    message: profileError.safeMessage,
  );
}

void main() {
  final repository = ProfileRepository();
  final cases = <String, ProfileErrorCode>{
    'missing': ProfileErrorCode.userNotFound,
    'duplicate': ProfileErrorCode.emailAlreadyUsed,
    'overloaded': ProfileErrorCode.serviceUnavailable,
    'broken': ProfileErrorCode.internalError,
  };

  for (final entry in cases.entries) {
    try {
      repository.loadName(entry.key);
      throw StateError('${entry.key} should fail');
    } catch (error) {
      final view = toViewError(error);
      final publicText = '${view.code} ${view.message}';

      assert(view.code == entry.value.name);
      assert(!publicText.contains('SQLSTATE'));
      assert(!publicText.contains('users_email_key'));
      assert(!publicText.contains('10.0.0.12'));
      assert(!publicText.contains('/srv/app'));
      assert(error is ProfileError && error.cause != null);
    }
  }
}
```

## 坑

- **把底层异常文案直接放进 SnackBar**：`error.toString()` 可能包含 SQL state、host、索引名、SDK 内部类型或平台路径。
- **用 HTTP status 代替领域错误码**：`500`、`409`、`404` 只能作为传输层提示，不能表达“邮箱已占用”“用户不存在”“限流中”等业务语义。
- **在 widget 里写字符串判断**：`if (message.contains('duplicate'))` 会让 UI 依赖后端或数据库文案，应该在 repository / adapter 边界翻译。
- **翻译时丢掉根因**：对外不能泄漏细节，但 `cause`、structured log、crash report breadcrumb 仍要保留，方便排障。
- **错误码和恢复动作脱节**：如果 `serviceUnavailable` 没有对应重试入口，`emailAlreadyUsed` 没有回到输入字段，错误码只是换了名字的字符串。

## 检查

- 搜索 UI 层是否还有 `toString()`、`DioException`、`PlatformException`、SQL state、Firebase raw code 直接进入用户可见文案。
- 抽样 3 个失败场景，确认 public view model 只包含稳定 `code` 和安全 `message`，底层 detail 只进入日志或 tracing。
- 给 adapter 边界补最小测试：底层 `row not found`、`unique violation`、`pool exhausted` 分别映射到不同领域错误码。
- 和 [`flutter-retry-policy-explicit-not-hidden-loop.md`](flutter-retry-policy-explicit-not-hidden-loop.md) 一起检查：哪些错误码允许重试，哪些错误码应引导用户修改输入或稍后再试。
- 对照 TypeScript 的 [`../typescript/external-error-codes-domain-defined-not-leaked.md`](../typescript/external-error-codes-domain-defined-not-leaked.md)、Python 的 [`../python/external-error-codes-domain-defined-not-leaked.md`](../python/external-error-codes-domain-defined-not-leaked.md) 和 Go 的 [`../go/external-error-codes-domain-defined-not-leaked.md`](../go/external-error-codes-domain-defined-not-leaked.md)，确认前后端对外错误码边界一致。
