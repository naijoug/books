# 对外错误码应由领域异常翻译，而不是泄漏底层异常

## 什么时候用

当 Python 服务需要把异常转换成 HTTP response、CLI exit code、webhook 回调或队列死信原因时。数据库驱动异常、第三方 SDK 错误字符串、文件路径和 stack trace 都应该留在日志里；对外契约应该只暴露稳定的领域错误码，例如 `USER_NOT_FOUND`、`EMAIL_ALREADY_USED`、`SERVICE_OVERLOADED`。

## 怎么写

```python
# external-error-codes-domain-defined-not-leaked.py
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ErrorCode(StrEnum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    EMAIL_ALREADY_USED = "EMAIL_ALREADY_USED"
    SERVICE_OVERLOADED = "SERVICE_OVERLOADED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppError(Exception):
    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class UserNotFoundError(AppError):
    def __init__(self, user_id: str) -> None:
        super().__init__(ErrorCode.USER_NOT_FOUND, "user not found")
        self.user_id = user_id


class EmailAlreadyUsedError(AppError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.EMAIL_ALREADY_USED, "email already used")


class ServiceOverloadedError(AppError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.SERVICE_OVERLOADED, "service overloaded")


class DatabaseError(Exception):
    pass


class RowNotFound(DatabaseError):
    pass


class UniqueViolation(DatabaseError):
    pass


class ConnectionPoolExhausted(DatabaseError):
    pass


@dataclass(frozen=True)
class PublicErrorResponse:
    status: int
    body: dict[str, str]


def translate_storage_error(error: DatabaseError, *, user_id: str) -> AppError:
    if isinstance(error, RowNotFound):
        return UserNotFoundError(user_id)
    if isinstance(error, UniqueViolation):
        return EmailAlreadyUsedError()
    if isinstance(error, ConnectionPoolExhausted):
        return ServiceOverloadedError()
    return AppError(ErrorCode.INTERNAL_ERROR, "internal server error")


def find_user(user_id: str) -> str:
    try:
        if user_id == "missing":
            raise RowNotFound("sql: no rows in result set")
        if user_id == "duplicate-email":
            raise UniqueViolation("SQLSTATE 23505 duplicate key users_email_key")
        if user_id == "overloaded":
            raise ConnectionPoolExhausted("db pool exhausted at 10.0.0.12")
        if user_id == "broken-db":
            raise DatabaseError("driver traceback: /srv/app/repository.py:17")
        return "Alice"
    except DatabaseError as error:
        # 用异常链保留根因给日志/observability，但对外响应只读 AppError.code/message。
        raise translate_storage_error(error, user_id=user_id) from error


def to_public_response(error: Exception) -> PublicErrorResponse:
    if not isinstance(error, AppError):
        error = AppError(ErrorCode.INTERNAL_ERROR, "internal server error")

    status_by_code = {
        ErrorCode.USER_NOT_FOUND: 404,
        ErrorCode.EMAIL_ALREADY_USED: 409,
        ErrorCode.SERVICE_OVERLOADED: 503,
        ErrorCode.INTERNAL_ERROR: 500,
    }
    return PublicErrorResponse(
        status=status_by_code[error.code],
        body={"code": error.code.value, "message": error.message},
    )


def _verify() -> None:
    assert find_user("ok") == "Alice"

    cases = {
        "missing": (404, "USER_NOT_FOUND"),
        "duplicate-email": (409, "EMAIL_ALREADY_USED"),
        "overloaded": (503, "SERVICE_OVERLOADED"),
        "broken-db": (500, "INTERNAL_ERROR"),
    }

    for user_id, (expected_status, expected_code) in cases.items():
        try:
            find_user(user_id)
        except Exception as error:  # noqa: BLE001 - 示例演示边界层统一翻译。
            response = to_public_response(error)
            public_text = str(response.body)
            assert response.status == expected_status
            assert response.body["code"] == expected_code
            assert "SQLSTATE" not in public_text
            assert "users_email_key" not in public_text
            assert "10.0.0.12" not in public_text
            assert "/srv/app" not in public_text
            if isinstance(error, AppError):
                assert isinstance(error.__cause__, DatabaseError)
        else:
            raise AssertionError(f"{user_id} should fail")


if __name__ == "__main__":
    _verify()
```

## 哪里容易错

1. **把异常类名直接当 code**：`IntegrityError`、`RowNotFound`、`ClientConnectorError` 是实现细节，不是产品契约。
2. **直接把 `str(error)` 放进响应**：底层异常字符串经常带 SQL state、索引名、主机地址、文件路径或 SDK 内部字段。
3. **翻译时丢掉异常链**：对外不能泄漏根因，但内部仍应使用 `raise AppError(...) from error` 保留排障线索。
4. **在 handler 里散落字符串判断**：`if "no rows" in str(error)` 会让错误契约依赖文案；应在 adapter 边界把底层异常翻译成领域异常。

## 一句话总结

Python 的 handler 不应该认识数据库异常和 SDK 文案；adapter 把底层异常翻译成领域异常，边界层只输出稳定 code 和安全 message，同时用异常链保留内部根因。
