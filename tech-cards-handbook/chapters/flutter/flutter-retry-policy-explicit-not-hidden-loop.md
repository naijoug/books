# 重试策略要显式化，而不是藏在按钮回调里

**问题**：Flutter 页面里常见的写法是用户点按钮后在 `onPressed`、`initState` 或 ViewModel 方法里临时写一个 `for` 循环重试网络请求。这样短期能“多试几次”，但后续很难看清哪些错误可重试、最多试几次、退避多久、取消页面后是否还会继续请求，以及重试耗尽后 UI 应该显示什么领域错误。

**要点**：

- 先把错误分成可重试、不可重试和调用方需要展示的领域错误；不要靠 `Exception.toString()` 或 HTTP 文本描述判断。
- 用 `RetryPolicy` 表达最大尝试次数和退避间隔，让策略能在测试里设成小值或零值。
- 重试函数只负责“按策略重新调用一次异步操作”；页面、ViewModel 或 repository adapter 仍负责把底层错误转换成领域错误。
- 每次退避前检查取消信号或页面生命周期；页面离开后不要继续悄悄重试并更新 UI。

| 维度 | 隐式循环 | 显式策略 |
|---|---|---|
| 可重试条件 | 写在按钮回调的 `catch` 里 | `isRetryable(error)` 单独定义 |
| 次数和退避 | 魔法数字散落在 widget / ViewModel | `RetryPolicy(maxAttempts, backoff)` |
| 生命周期 | 页面 dispose 后仍可能完成回调 | 调用方用取消标记或 `mounted` 拦截结果 |
| 耗尽语义 | 直接显示底层错误字符串 | 返回稳定的领域错误给 UI 决策 |

**示例**：

```dart
import 'dart:async';

sealed class ProfileError implements Exception {}

final class TemporaryProfileFailure extends ProfileError {}
final class ProfileForbidden extends ProfileError {}

final class RetryExhausted extends ProfileError {
  RetryExhausted(this.lastError, this.attempts);

  final Object lastError;
  final int attempts;
}

class RetryPolicy {
  const RetryPolicy({this.maxAttempts = 3, this.backoff = Duration.zero});

  final int maxAttempts;
  final Duration backoff;
}

typedef Cancelled = bool Function();

bool isRetryable(Object error) => error is TemporaryProfileFailure;

Future<T> withRetry<T>(
  RetryPolicy policy,
  Future<T> Function() operation, {
  Cancelled isCancelled = _neverCancelled,
}) async {
  Object? lastError;
  final attempts = policy.maxAttempts < 1 ? 1 : policy.maxAttempts;

  for (var attempt = 1; attempt <= attempts; attempt++) {
    if (isCancelled()) {
      throw StateError('operation cancelled');
    }

    try {
      return await operation();
    } catch (error) {
      if (!isRetryable(error)) {
        rethrow;
      }

      lastError = error;
      if (attempt < attempts && policy.backoff > Duration.zero) {
        await Future<void>.delayed(policy.backoff);
      }
    }
  }

  throw RetryExhausted(lastError!, attempts);
}

bool _neverCancelled() => false;

Future<String> fetchProfile() async {
  var attempts = 0;
  return withRetry(
    const RetryPolicy(maxAttempts: 3),
    () async {
      attempts += 1;
      if (attempts < 3) {
        throw TemporaryProfileFailure();
      }
      return 'profile-data';
    },
  );
}
```

在 widget 或 ViewModel 中使用时，重试函数只返回结果或领域错误；UI 仍要在写入状态前检查 `mounted`、取消标记或当前请求 token，避免旧请求覆盖新页面状态。

**坑**：

- 在 `onPressed` 里直接写 `for (var i = 0; i < 3; i++)`，后续其它入口复制出不同重试次数。
- 用 `error.toString().contains('timeout')` 判断是否重试；SDK 文案一变，恢复策略就失效。
- 页面 dispose 后重试仍在后台完成，随后调用 `setState` 或更新已过期的状态对象。
- 重试耗尽后把最后一个底层异常直接显示给用户，泄漏 SDK、HTTP 或存储实现细节。
- 对权限、参数错误这类不可重试失败继续重试，放大无意义流量并拖慢用户反馈。

**检查**：

- 可重试错误集合是否由稳定类型或领域错误码定义，而不是字符串匹配？
- 最大尝试次数和退避间隔是否集中在 `RetryPolicy`，测试里能否设成 `maxAttempts: 1` 或 `Duration.zero`？
- 重试耗尽后，UI 是否收到稳定领域错误，而不是底层 SDK 异常文本？
- 页面离开、请求被替换或 widget 已不再 `mounted` 时，异步结果是否会被丢弃而不是继续写状态？

**对照阅读**：

- Swift 显式重试：[`../swift/swift-retry-policy-explicit-not-hidden-loop.md`](../swift/swift-retry-policy-explicit-not-hidden-loop.md)
- TypeScript 显式重试：[`../typescript/retry-policy-explicit-not-hidden-catch.md`](../typescript/retry-policy-explicit-not-hidden-catch.md)
- Python 显式重试：[`../python/retry-policy-explicit-not-hidden-loop.md`](../python/retry-policy-explicit-not-hidden-loop.md)
