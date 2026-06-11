# 降级策略应在调用方决定，而不是被调方隐藏

## 什么时候用

当 Python service 依赖缓存、画像服务、推荐服务、第三方 API 或搜索服务时。被调方只应该返回真实结果或抛出可分类异常；是否用默认值、缓存、简化响应继续服务，必须由调用方按业务场景决定。

典型判断：同一个 `ProfileClient` 超时，在推荐页可以降级成“匿名用户”，在支付风控里必须中断。把降级藏在 client 里，会让上层永远分不清“真的没有数据”和“依赖失败后被伪装成空数据”。

## 怎么写

```python
# degradation-strategy-at-caller-not-callee.py
from __future__ import annotations

from dataclasses import dataclass


class ProfileError(Exception):
    pass


class ProfileNotFoundError(ProfileError):
    pass


class ProfileServiceUnavailableError(ProfileError):
    pass


@dataclass(frozen=True)
class Profile:
    user_id: str
    display_name: str
    verified: bool


@dataclass(frozen=True)
class DisplayNameResult:
    value: str
    degraded: bool


class ProfileClient:
    def fetch(self, user_id: str) -> Profile:
        # 被调方只报告事实：成功返回 Profile，失败抛出可分类异常。
        # 不要在这里返回 Profile(user_id, "anonymous", False) 伪装成功。
        if user_id == "missing":
            raise ProfileNotFoundError("profile not found")
        if user_id == "timeout":
            raise ProfileServiceUnavailableError("profile service timeout")
        return Profile(user_id=user_id, display_name="Ada", verified=True)


class RecommendationService:
    def __init__(self, client: ProfileClient) -> None:
        self.client = client

    def display_name_for_card(self, user_id: str) -> DisplayNameResult:
        try:
            profile = self.client.fetch(user_id)
        except ProfileNotFoundError:
            # 推荐卡片允许“用户缺少画像”降级，但必须标记 degraded。
            return DisplayNameResult(value="anonymous", degraded=True)
        except ProfileServiceUnavailableError as error:
            # 依赖故障不是“没有画像”，继续传播给上层重试/熔断/告警。
            raise ProfileServiceUnavailableError(
                f"cannot render recommendation card for {user_id}"
            ) from error
        return DisplayNameResult(value=profile.display_name, degraded=False)


class PaymentRiskService:
    def __init__(self, client: ProfileClient) -> None:
        self.client = client

    def verified_profile(self, user_id: str) -> Profile:
        try:
            return self.client.fetch(user_id)
        except ProfileError as error:
            # 支付风控不能用默认画像继续走；这里必须保留异常链并中断。
            raise ProfileError(f"cannot verify payer profile for {user_id}") from error


def _verify() -> None:
    client = ProfileClient()
    recommendation = RecommendationService(client)
    payment = PaymentRiskService(client)

    ok = recommendation.display_name_for_card("u-1")
    assert ok == DisplayNameResult(value="Ada", degraded=False)

    fallback = recommendation.display_name_for_card("missing")
    assert fallback == DisplayNameResult(value="anonymous", degraded=True)

    try:
        recommendation.display_name_for_card("timeout")
    except ProfileServiceUnavailableError as error:
        assert isinstance(error.__cause__, ProfileServiceUnavailableError)
        assert "recommendation card" in str(error)
    else:
        raise AssertionError("service outage must not be silently degraded")

    try:
        payment.verified_profile("missing")
    except ProfileError as error:
        assert isinstance(error.__cause__, ProfileNotFoundError)
        assert "verify payer profile" in str(error)
    else:
        raise AssertionError("payment risk must not use fake profile")


if __name__ == "__main__":
    _verify()
```

## 要点

- 被调方（client / repository / SDK adapter）只负责把底层失败翻译成可分类异常，不负责替上层选择默认值。
- 调用方按业务语义显式决定：哪些异常可以降级，哪些异常必须传播。
- 降级结果要可观测，例如返回 `degraded=True`、打 metric、写日志或 trace tag。
- 不可降级路径仍要用 `raise ... from error` 保留异常链，方便上层 handler / CLI 继续分类。

## 容易踩坑

- **在 client 里返回空对象**：`return Profile(user_id, "", False)` 会把 404、timeout、decode error 混成同一种“空画像”。
- **裸 `except ProfileError` 后统一降级**：推荐页可以降级，不代表支付、风控、发货也可以降级。
- **降级但不标记**：调用方和观测系统看不到默认值来源，事故时无法判断影响面。
- **把异常链截断**：重新抛出 `ProfileError("failed")` 但不用 `from error`，上层无法知道根因是 not found 还是 timeout。

## 检查

- 搜索 client / repository 是否在异常分支返回默认对象、空列表或空字符串。
- 对每个调用方列出“可降级异常”和“必须传播异常”，不要只写一个大 `except`。
- 验证降级响应包含可观测标记；不可降级响应保留 `__cause__`。
- 运行示例：`python3 degradation-strategy-at-caller-not-callee.py`。

## 延伸阅读

- Go 对照：[`../go/degradation-strategy-at-caller-not-callee.md`](../go/degradation-strategy-at-caller-not-callee.md)
- Rust 对照：[`../rust/degradation-strategy-at-caller-not-callee.md`](../rust/degradation-strategy-at-caller-not-callee.md)
