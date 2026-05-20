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
    if not 0 <= discount <= 1:
        raise ValueError("discount must be between 0 and 1")
    return round(price * (1 - discount))

@pytest.mark.parametrize(
    ("price", "discount", "expected"),
    [(100, 0.2, 80), (99, 0, 99), (99, 1, 0)],
)
def test_price_after_discount(price, discount, expected):
    assert price_after_discount(price, discount) == expected

def test_invalid_discount():
    with pytest.raises(ValueError):
        price_after_discount(100, 1.5)
```

**坑**：测试过度绑定内部调用顺序，会让合理重构变得困难。

**检查**：如果换一种实现但行为不变，测试是否仍然应该通过？答案应该是“是”。
