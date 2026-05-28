# 测试先覆盖行为，再覆盖实现细节

**问题**：为什么测试写了很多，重构还是容易坏？

**要点**：

- 测试应该描述外部可观察行为。
- 少测私有函数，多测输入输出、异常、边界条件。
- 使用参数化测试减少重复。

**示例**：

```python
import pytest


def price_after_discount(price: int, discount: float) -> int:
    """Return the rounded final price after applying a percentage discount."""
    if price < 0:
        raise ValueError("price must be non-negative")
    if not 0 <= discount <= 1:
        raise ValueError("discount must be between 0 and 1")
    return round(price * (1 - discount))


@pytest.mark.parametrize(
    ("price", "discount", "expected"),
    [
        (100, 0.2, 80),
        (99, 0, 99),
        (99, 1, 0),
        (199, 0.152, 169),  # 只锁定对外承诺：四舍五入后的最终价格
    ],
)
def test_price_after_discount(price, discount, expected):
    assert price_after_discount(price, discount) == expected


@pytest.mark.parametrize("discount", [-0.01, 1.01])
def test_invalid_discount(discount):
    with pytest.raises(ValueError, match="discount"):
        price_after_discount(100, discount)


def test_invalid_price():
    with pytest.raises(ValueError, match="non-negative"):
        price_after_discount(-1, 0.2)
```

把代码保存为 `tests-cover-behavior-first.py` 后运行（若本机已安装 pytest，也可以用 `python3 -m pytest -q tests-cover-behavior-first.py`）：

```bash
uv run --with pytest python -m pytest -q tests-cover-behavior-first.py
```

反向检查：如果把 `return round(price * (1 - discount))` 改成 `return int(price * (1 - discount))`，`(199, 0.152, 169)` 这组行为测试应该失败；如果只是把内部实现拆成私有辅助函数，但输入输出和异常不变，测试仍应通过。

**坑**：测试过度绑定内部调用顺序，会让合理重构变得困难；只测 happy path，又会让边界和异常在重构时偷偷坏掉。

**检查**：如果换一种实现但行为不变，测试是否仍然应该通过？答案应该是“是”。如果某个公开边界（折扣范围、负价格、舍入规则）改变，是否有测试第一时间失败？答案也应该是“是”。
