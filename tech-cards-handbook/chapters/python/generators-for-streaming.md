# 生成器适合流式处理，不适合重复遍历

**问题**：大文件或长序列要如何避免一次性加载进内存？

**要点**：

- `yield` 每次产出一个值，调用方按需消费。
- 生成器只能自然遍历一次。
- 适合日志过滤、分页读取、流水线转换。

**示例**：

```python
from pathlib import Path
from tempfile import NamedTemporaryFile


def read_errors(lines):
    """逐行检查，只产出含 ERROR 的行。"""
    for line in lines:
        if "ERROR" in line:
            yield line.strip()


# ---------- 正向：过滤正确 ----------
log_lines = [
    "2026-05-28 INFO  started\n",
    "2026-05-28 ERROR disk full\n",
    "2026-05-28 WARN  retrying\n",
    "2026-05-28 ERROR timeout\n",
    "2026-05-28 INFO  done\n",
]

errors = list(read_errors(log_lines))
assert errors == ["2026-05-28 ERROR disk full", "2026-05-28 ERROR timeout"]

# ---------- 单次遍历：生成器耗尽 ----------
gen = read_errors(log_lines)
first_pass = list(gen)
second_pass = list(gen)
assert first_pass == errors
assert second_pass == [], "生成器只能遍历一次，第二次为空"

# ---------- 流水线：生成器组合 ----------
def strip_timestamp(lines):
    for line in lines:
        yield line.split(" ", 1)[1] if " " in line else line

raw_errors = read_errors(log_lines)
messages = list(strip_timestamp(raw_errors))
assert messages == ["ERROR disk full", "ERROR timeout"]

# ---------- 反向：多消费者共享同一生成器会丢数据 ----------
shared_gen = read_errors(log_lines)
consumer_a = next(shared_gen)
consumer_b_lines = list(shared_gen)
assert consumer_a == "2026-05-28 ERROR disk full"
assert consumer_b_lines == ["2026-05-28 ERROR timeout"], (
    "consumer_b 只能拿到 consumer_a 取走后的剩余"
)

# ---------- 文件路径版本 ----------
def read_errors_from_file(path: Path):
    with path.open() as f:
        for line in f:
            if "ERROR" in line:
                yield line.strip()

with NamedTemporaryFile(mode="w", suffix=".log", delete=False) as tmp:
    tmp.writelines(log_lines)
    tmp_path = Path(tmp.name)

file_errors = list(read_errors_from_file(tmp_path))
assert file_errors == ["2026-05-28 ERROR disk full", "2026-05-28 ERROR timeout"]
tmp_path.unlink()
```

**坑**：把生成器传给多个消费者时，后面的消费者可能拿不到数据——上面 `shared_gen` 示例展示了只有第一个消费者取走的数据之后才剩余给后者。需要重复遍历时，用 `list()` 物化或重新创建生成器。

**检查**：把代码保存为 `generators-for-streaming.py` 后运行 `python3 generators-for-streaming.py`；正向过滤、单次遍历耗尽、流水线组合、多消费者竞争和文件读取五组断言都应通过且无输出。
