# 生成器适合流式处理，不适合重复遍历

**问题**：大文件或长序列要如何避免一次性加载进内存？

**要点**：

- `yield` 每次产出一个值，调用方按需消费。
- 生成器只能自然遍历一次。
- 适合日志处理、分页读取、流水线转换。

**示例**：

```python
from pathlib import Path

def read_errors(path: Path):
    with path.open() as file:
        for line in file:
            if "ERROR" in line:
                yield line.strip()

for error in read_errors(Path("app.log")):
    print(error)
```

**坑**：把生成器传给多个消费者时，后面的消费者可能拿不到数据。需要重复遍历时，用列表或重新创建生成器。

**检查**：如果数据量很大且只需要顺序消费，优先考虑生成器。
