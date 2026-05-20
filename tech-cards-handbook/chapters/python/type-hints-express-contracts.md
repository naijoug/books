# 类型标注用于表达契约，不是替代测试

**问题**：Python 是动态语言，为什么还要写类型？

**要点**：

- 类型标注帮助 IDE、静态检查器和读代码的人理解边界。
- 优先标注函数参数、返回值和核心数据结构。
- 复杂类型可以用 `TypedDict`、`Protocol` 或 dataclass 表达。

**示例**：

```python
from typing import TypedDict

class UserRow(TypedDict):
    id: int
    email: str
    active: bool

def active_emails(users: list[UserRow]) -> list[str]:
    return [user["email"] for user in users if user["active"]]
```

**坑**：类型不会在运行时自动验证外部输入。API 请求、JSON、CSV 仍需要显式校验。

**检查**：公共函数是否能只看签名就知道输入输出？如果不能，先补类型。
