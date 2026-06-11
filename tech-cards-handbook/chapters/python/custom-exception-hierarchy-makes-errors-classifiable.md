# 自定义异常层级让错误可分类

## 一句话

不要到处 `raise ValueError` 和 `raise RuntimeError`；用领域异常类表达"失败是什么"，让调用方按类型和层级 `except`，而不是靠字符串匹配或 `e.args` 拆解错误。

## 什么时候用

- 函数需要返回不同种类的失败，调用方要区分"重试"、"降级"、"用户输入错"和"系统故障"。
- 捕获底层异常后要换成业务语义再抛出，但 `raise ValueError("...")` 丢失了分类能力。
- 多个模块各自抛异常，上层需要统一捕获某一类而不是逐个列举。

## 怎么写

```python
# === 定义 ===

class AppError(Exception):
    """所有业务异常的基类。携带错误码和可读消息。"""
    def __init__(self, code: str, message: str, *, cause: Exception | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.__cause__ = cause  # 保留原始异常链，等价于 raise ... from ...

class NotFoundError(AppError):
    """资源不存在。不可重试。"""
    def __init__(self, resource: str, id_: str, *, cause: Exception | None = None):
        super().__init__(
            code=f"{resource.upper()}_NOT_FOUND",
            message=f"{resource} '{id_}' 不存在",
            cause=cause,
        )

class RateLimitError(AppError):
    """上游限流。可重试。"""
    def __init__(self, service: str, retry_after: int, *, cause: Exception | None = None):
        super().__init__(
            code="RATE_LIMITED",
            message=f"{service} 限流，{retry_after}s 后可重试",
            cause=cause,
        )
        self.retry_after = retry_after


# === 使用 ===

class _UpstreamError(Exception):
    """模拟上游 HTTP 错误。"""
    def __init__(self, status: int, headers: dict | None = None):
        super().__init__(f"HTTP {status}")
        self.status = status
        self.headers = headers or {}


def fetch_profile(user_id: str) -> dict:
    """从上游服务获取用户资料。底层异常被翻译成领域异常。"""
    # 模拟：user_id 以 "fail" 开头表示不存在，以 "rate" 开头表示限流
    if user_id.startswith("fail"):
        e = _UpstreamError(404)
        raise NotFoundError("user", user_id, cause=e) from e
    if user_id.startswith("rate"):
        e = _UpstreamError(429, {"Retry-After": "30"})
        raise RateLimitError("profile-service", 30, cause=e) from e
    if user_id.startswith("net"):
        e = ConnectionError("timeout")
        raise AppError("NETWORK_ERROR", f"无法连接 profile-service: {e}", cause=e) from e
    return {"display_name": f"User-{user_id}"}


# === 调用方按类型分支 ===

def get_display_name(user_id: str) -> str:
    """调用方根据异常类型决定降级还是传播。"""
    try:
        profile = fetch_profile(user_id)
        return profile["display_name"]
    except NotFoundError:
        # 可降级：用户不存在时显示占位名
        return f"user-{user_id}"
    except RateLimitError as e:
        # 可降级但需标记：限流时返回占位名并记日志
        print(f"[warn] 限流降级: {e.message}")
        return f"user-{user_id} (degraded)"
    # 其他 AppError 不捕获，继续向上传播


# === 验证断言 ===

def _verify():
    assert issubclass(NotFoundError, AppError)
    assert issubclass(RateLimitError, AppError)
    assert not issubclass(NotFoundError, RateLimitError)

    try:
        raise NotFoundError("user", "u-123")
    except AppError as e:
        assert e.code == "USER_NOT_FOUND"
        assert "u-123" in e.args[0]
    else:
        assert False, "应该抛出 NotFoundError"

    rl = RateLimitError("svc", 30)
    assert rl.retry_after == 30
    assert isinstance(rl, AppError)
    assert rl.message == "svc 限流，30s 后可重试"

    assert get_display_name("u-1") == "User-u-1"
    assert get_display_name("fail-1") == "user-fail-1"
    assert get_display_name("rate-1") == "user-rate-1 (degraded)"

    original = ConnectionError("timeout")
    wrapped = AppError("NET", "网络错误", cause=original)
    assert wrapped.__cause__ is original

    print("✅ custom-exception-hierarchy: all checks passed")


_verify()
```

## 哪里容易错

| 陷阱 | 问题 | 修正 |
|---|---|---|
| 只用内置异常 | `ValueError`、`RuntimeError` 无法区分业务语义，调用方只能靠消息文本判断 | 定义 `AppError` 子类，让 `isinstance` 和 `except` 直接分类 |
| 捕获后重新抛出丢失根因 | `raise AppError(...)` 不带 `from e`，`__cause__` 断链 | 用 `raise ... from e` 保留异常链 |
| 异常层级太深 | 继承 4-5 层，调用方记不住层级关系 | 控制在 2-3 层：`AppError` → 领域分类 → 具体异常 |
| 在异常里塞业务逻辑 | `__init__` 里做数据库查询或网络请求 | 异常只携带纯数据（code、message、cause），逻辑在捕获方 |
| `except Exception` 吞掉所有 | 上层无法区分可恢复和不可恢复错误 | 按 `AppError` 子类精确捕获，或显式 `raise` 传播 |

## 验证

```bash
python3 custom-exception-hierarchy-makes-errors-classifiable.py
```

## 对照阅读

- Go: [`go/error-wrapping-vs-result-propagation.md`](../go/error-wrapping-vs-result-propagation.md) — Go 用 `errors.Is`/`errors.As` 分类，Python 用 `isinstance`/`except` 子类。
- Rust: [`rust/result-means-failable-with-reason.md`](../rust/result-means-failable-with-reason.md) — Rust 用 `Result` 和 `match` 分支，Python 用异常层级和 `try/except`。
