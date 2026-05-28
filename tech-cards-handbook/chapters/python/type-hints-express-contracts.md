# 类型标注用于表达契约，不是替代测试

**问题**：Python 是动态语言，为什么还要写类型？

**要点**：

- 类型标注帮助 IDE、静态检查器和读代码的人理解边界。
- 优先标注函数参数、返回值和核心数据结构。
- 复杂类型可以用 `TypedDict`、`Protocol` 或 dataclass 表达。

**示例**：

```python
from typing import List, Protocol, Sequence, Tuple, TypedDict

class UserRow(TypedDict):
    id: int
    email: str
    active: bool

class Mailer(Protocol):
    def send(self, to: str, subject: str) -> None:
        ...

def active_emails(users: Sequence[UserRow]) -> List[str]:
    return [user["email"] for user in users if user["active"]]

def notify_active_users(users: Sequence[UserRow], mailer: Mailer) -> int:
    emails = active_emails(users)
    for email in emails:
        mailer.send(email, "Welcome back")
    return len(emails)

def parse_user(raw: object) -> UserRow:
    if not isinstance(raw, dict):
        raise ValueError("user must be an object")

    user_id = raw.get("id")
    email = raw.get("email")
    active = raw.get("active")
    if not isinstance(user_id, int):
        raise ValueError("id must be int")
    if not isinstance(email, str):
        raise ValueError("email must be str")
    if not isinstance(active, bool):
        raise ValueError("active must be bool")

    return {"id": user_id, "email": email, "active": active}

class RecordingMailer:
    def __init__(self) -> None:
        self.sent: List[Tuple[str, str]] = []

    def send(self, to: str, subject: str) -> None:
        self.sent.append((to, subject))

rows: List[UserRow] = [
    {"id": 1, "email": "ada@example.com", "active": True},
    {"id": 2, "email": "grace@example.com", "active": False},
]
mailer = RecordingMailer()

assert active_emails(rows) == ["ada@example.com"]
assert notify_active_users(rows, mailer) == 1
assert mailer.sent == [("ada@example.com", "Welcome back")]
assert parse_user({"id": 3, "email": "linus@example.com", "active": True})["email"] == "linus@example.com"

try:
    parse_user({"id": "3", "email": "linus@example.com", "active": True})
except ValueError as exc:
    assert "id must be int" in str(exc)
else:
    raise AssertionError("invalid external input should be rejected")

# 取消下一行注释后，静态检查器应报错：id 需要 int，而不是 str。
# bad_rows: List[UserRow] = [{"id": "1", "email": "bad@example.com", "active": True}]
```

把代码保存为 `type-hints-express-contracts.py` 后运行 `python3 type-hints-express-contracts.py`，应无输出且退出码为 0；再运行 `npx -y pyright@1.1.407 type-hints-express-contracts.py`，应得到 `0 errors`。如果取消 `bad_rows` 那行注释，`pyright` 应报告 `id` 字段类型不匹配。

**坑**：类型不会在运行时自动验证外部输入。API 请求、JSON、CSV 仍需要 `parse_user()` 这类显式校验；`TypedDict` 只是在静态检查阶段约束字典形状，不会拦截运行时传入的脏数据。

**检查**：公共函数是否能只看签名就知道输入输出？如果不能，先补类型；但凡数据跨过系统边界，是否同时有运行时校验和测试？
