# 错误恢复路径需要一张决策表串起来

**问题**：自定义异常、重试、降级和对外错误码如果分别写在不同函数里，单看每一段都像是正确的；但真正出事故时，调用方仍可能不知道“这个错误该重试、降级、返回 404，还是报警”。错误恢复路径需要一张决策表，把错误分类、恢复动作和对外契约串成同一条可审查链路。

**要点**：

- 先列出领域错误类型，而不是从 handler 或日志里反推错误含义。
- 每个错误类型只对应一个默认恢复动作：重试、降级、直接返回用户可见错误，或升级为内部故障。
- 重试和降级都要写成显式字段，避免藏在 `except` 分支或 adapter 默认值里。
- 对外响应只读取领域错误码和安全消息；底层异常、SQL state、SDK 类型名只进日志或 `__cause__`。

| 维度 | 零散异常处理 | 决策表 |
|---|---|---|
| 错误分类 | 多个 `except` 分支各写各的 | 领域错误类型统一登记 |
| 调用方动作 | 临时判断是否重试/降级 | `action` 字段明确表达 |
| 对外契约 | handler 拼接异常字符串 | `public_code` / `public_message` 稳定输出 |
| 审查方式 | 只能读完整调用链 | 一张表就能发现缺口 |

**示例**：

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RecoveryAction(StrEnum):
    RETRY = "retry"
    DEGRADE = "degrade"
    RETURN_PUBLIC_ERROR = "return_public_error"
    ESCALATE = "escalate"


class ErrorCode(StrEnum):
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    PROFILE_TEMPORARILY_UNAVAILABLE = "PROFILE_TEMPORARILY_UNAVAILABLE"
    INTERNAL = "INTERNAL"


class ProfileError(Exception):
    code: ErrorCode
    safe_message: str

    def __init__(self, message: str, *, safe_message: str) -> None:
        super().__init__(message)
        self.safe_message = safe_message


class ProfileNotFoundError(ProfileError):
    code = ErrorCode.PROFILE_NOT_FOUND


class TemporaryProfileError(ProfileError):
    code = ErrorCode.PROFILE_TEMPORARILY_UNAVAILABLE


class ProfileCorruptedError(ProfileError):
    code = ErrorCode.INTERNAL


@dataclass(frozen=True)
class RecoveryDecision:
    action: RecoveryAction
    public_code: ErrorCode
    public_message: str
    retryable: bool = False
    degraded: bool = False


DECISION_TABLE: dict[type[ProfileError], RecoveryDecision] = {
    ProfileNotFoundError: RecoveryDecision(
        action=RecoveryAction.RETURN_PUBLIC_ERROR,
        public_code=ErrorCode.PROFILE_NOT_FOUND,
        public_message="profile not found",
    ),
    TemporaryProfileError: RecoveryDecision(
        action=RecoveryAction.RETRY,
        public_code=ErrorCode.PROFILE_TEMPORARILY_UNAVAILABLE,
        public_message="profile service is temporarily unavailable",
        retryable=True,
    ),
    ProfileCorruptedError: RecoveryDecision(
        action=RecoveryAction.ESCALATE,
        public_code=ErrorCode.INTERNAL,
        public_message="internal error",
    ),
}


def decide_recovery(error: ProfileError) -> RecoveryDecision:
    for error_type, decision in DECISION_TABLE.items():
        if isinstance(error, error_type):
            return decision
    return RecoveryDecision(
        action=RecoveryAction.ESCALATE,
        public_code=ErrorCode.INTERNAL,
        public_message="internal error",
    )


def display_name_or_degrade(error: ProfileError) -> tuple[str, RecoveryDecision]:
    decision = decide_recovery(error)
    if isinstance(error, ProfileNotFoundError):
        return "anonymous", RecoveryDecision(
            action=RecoveryAction.DEGRADE,
            public_code=decision.public_code,
            public_message=decision.public_message,
            degraded=True,
        )
    raise error


def to_public_response(error: ProfileError) -> dict[str, str]:
    decision = decide_recovery(error)
    return {"code": decision.public_code, "message": decision.public_message}


def _verify() -> None:
    not_found = ProfileNotFoundError(
        "profile row missing: SELECT * FROM profiles WHERE id='42'",
        safe_message="profile not found",
    )
    name, decision = display_name_or_degrade(not_found)
    assert name == "anonymous"
    assert decision.degraded is True
    assert decision.action == RecoveryAction.DEGRADE

    temporary = TemporaryProfileError(
        "profile sdk timeout: host=10.0.0.8, trace=abc",
        safe_message="profile service is temporarily unavailable",
    )
    retry_decision = decide_recovery(temporary)
    assert retry_decision.retryable is True
    assert retry_decision.action == RecoveryAction.RETRY

    response = to_public_response(temporary)
    assert response == {
        "code": ErrorCode.PROFILE_TEMPORARILY_UNAVAILABLE,
        "message": "profile service is temporarily unavailable",
    }
    assert "10.0.0.8" not in str(response)
    assert "trace=abc" not in str(response)

    corrupted = ProfileCorruptedError(
        "json decode failed at /var/lib/profiles/42.json",
        safe_message="internal error",
    )
    assert decide_recovery(corrupted).action == RecoveryAction.ESCALATE
    assert "/var/lib" not in str(to_public_response(corrupted))


if __name__ == "__main__":
    _verify()
    print("error recovery decision table keeps actions explicit")
```

**坑**：

- 只新增异常类型，不更新决策表，导致 handler 走默认 500 或暴露底层异常。
- 把重试次数、降级默认值和对外错误码分别写在三个函数里，review 时看不出它们是否一致。
- 对同一个错误既重试又降级，但没有记录先后顺序，线上表现随调用路径变化。
- 决策表只写对外 code，不写调用方动作，结果业务层仍要靠字符串或 SDK 类型判断。

**检查**：

- 每个领域错误是否都能在一张表里看到默认恢复动作、是否可重试、是否可降级和对外错误码？
- handler / CLI 是否只从决策表读取安全 `public_code` / `public_message`？
- adapter 是否仍用 `raise ... from error` 保留底层根因，但不把根因传给对外响应？
- 新增错误类型时，验证脚本是否能失败提示“决策表未覆盖”？

**延伸阅读**：

- Python 错误分类：[`custom-exception-hierarchy-makes-errors-classifiable.md`](custom-exception-hierarchy-makes-errors-classifiable.md)
- Python 显式重试：[`retry-policy-explicit-not-hidden-loop.md`](retry-policy-explicit-not-hidden-loop.md)
- Python 调用方降级：[`degradation-strategy-at-caller-not-callee.md`](degradation-strategy-at-caller-not-callee.md)
- Python 对外错误码：[`external-error-codes-domain-defined-not-leaked.md`](external-error-codes-domain-defined-not-leaked.md)
