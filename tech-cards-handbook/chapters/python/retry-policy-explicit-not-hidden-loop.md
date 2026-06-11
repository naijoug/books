# 重试策略要显式化，而不是藏在异常处理循环里

**问题**：调用 HTTP API、数据库、队列或文件系统失败时，什么时候应该重试？如果把 `for`/`while` 循环直接塞进 `except` 分支，后续很难看清哪些异常可重试、最多试几次、退避多久，以及重试耗尽后调用方会收到什么领域错误。

**要点**：

- 先用自定义异常层级区分可重试错误和不可重试错误；不要靠 `"timeout" in str(error)` 判断。
- 用 `RetryPolicy` 之类的小对象表达最大次数和退避间隔，让策略能被测试、配置和复用。
- 重试函数只负责“按策略重新执行一次操作”；业务函数仍负责把底层异常翻译成领域异常。
- 重试耗尽后抛出稳定的领域异常，并用 `raise ... from error` 保留最后一次根因。

| 维度 | 隐式异常循环 | 显式策略 |
|---|---|---|
| 可重试条件 | 散落在多个 `except` 分支 | `is_retryable(error)` 单独定义 |
| 次数和退避 | 魔法数字写在循环体 | `RetryPolicy(max_attempts, backoff_seconds)` |
| 测试方式 | 依赖真实 sleep 和真实下游 | 注入假操作和零退避 |
| 耗尽语义 | 抛出最后一个底层异常 | 抛出领域异常并保留 `__cause__` |

**示例**：

```python
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


class ProfileError(Exception):
    """所有 profile 读取失败的领域基类。"""


class TemporaryProfileError(ProfileError):
    """网络抖动、限流、连接池耗尽等可重试失败。"""


class ProfileNotFoundError(ProfileError):
    """用户不存在，重试没有意义。"""


class ProfileUnavailableError(ProfileError):
    """重试耗尽后交给上层分类处理的稳定领域错误。"""


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int
    backoff_seconds: float = 0

    def normalized(self) -> "RetryPolicy":
        return RetryPolicy(max(1, self.max_attempts), max(0, self.backoff_seconds))


def is_retryable(error: Exception) -> bool:
    return isinstance(error, TemporaryProfileError)


def with_retry(
    policy: RetryPolicy,
    operation: Callable[[], str],
    sleep: Callable[[float], None] = lambda _: None,
) -> str:
    policy = policy.normalized()
    last_retryable_error: Exception | None = None

    for attempt in range(1, policy.max_attempts + 1):
        try:
            return operation()
        except Exception as error:
            if not is_retryable(error):
                raise

            last_retryable_error = error
            if attempt < policy.max_attempts:
                sleep(policy.backoff_seconds)

    raise ProfileUnavailableError(
        f"profile service unavailable after {policy.max_attempts} attempts"
    ) from last_retryable_error


def fetch_profile_name(user_id: str, failures_before_success: int) -> str:
    attempts = 0

    def call_profile_service() -> str:
        nonlocal attempts
        attempts += 1
        if user_id == "missing":
            raise ProfileNotFoundError("profile missing")
        if attempts <= failures_before_success:
            raise TemporaryProfileError(f"temporary timeout on attempt {attempts}")
        return f"user-{user_id}"

    return with_retry(RetryPolicy(max_attempts=3), call_profile_service)


def _verify() -> None:
    assert fetch_profile_name("42", failures_before_success=2) == "user-42"

    try:
        fetch_profile_name("missing", failures_before_success=0)
    except ProfileNotFoundError:
        pass
    else:
        raise AssertionError("not found must not be retried or hidden")

    try:
        fetch_profile_name("slow", failures_before_success=3)
    except ProfileUnavailableError as error:
        assert isinstance(error.__cause__, TemporaryProfileError)
        assert "after 3 attempts" in str(error)
    else:
        raise AssertionError("retry exhaustion must become a domain error")


if __name__ == "__main__":
    _verify()
    print("retry policy keeps retry decisions explicit")
```

**坑**：

- 在 `except TimeoutError` 里直接 `continue`，导致最大次数、退避和可重试集合散落在业务函数里。
- 用字符串匹配异常消息判断是否重试；底层 SDK 文案一变，恢复策略就失效。
- 重试耗尽后直接抛出最后一个底层异常，让 handler 只能看见 SDK/数据库细节，不能输出稳定错误码。
- 对 `ProfileNotFoundError`、权限错误、参数错误也重试，放大下游压力并掩盖真正的调用方问题。

**检查**：

- 可重试异常集合是否由稳定异常类型或领域错误码定义，而不是靠字符串判断？
- 最大尝试次数、退避间隔和 sleep 函数是否能在测试里设成小值或零值？
- 重试耗尽后，上层是否收到稳定领域异常，同时还能通过 `__cause__` 找到最后一次根因？
- handler / CLI 对外输出是否只暴露安全错误码，而不是直接拼接底层异常字符串？

**延伸阅读**：

- Go 对照：[`../go/retry-policy-explicit-not-hidden-loop.md`](../go/retry-policy-explicit-not-hidden-loop.md)
- Rust 对照：[`../rust/retry-strategy-explicit-not-implicit-loop.md`](../rust/retry-strategy-explicit-not-implicit-loop.md)
