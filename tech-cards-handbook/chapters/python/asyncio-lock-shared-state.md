# `asyncio.Lock` 保护共享状态

**问题**：单线程事件循环里为什么还会有竞态条件？

**要点**：

- 只要在“读-改-写”中间出现 `await`，其他任务就可能插入。
- `Lock` 保护的是临界区，不是整个函数。
- 临界区越短越好。

**示例**：

```python
import asyncio

class SharedCounter:
    def __init__(self) -> None:
        self.value = 0
        self.lock = asyncio.Lock()

    async def increment(self) -> None:
        async with self.lock:
            current = self.value
            await asyncio.sleep(0)  # yield point inside critical section
            self.value = current + 1

    async def unsafe_increment(self) -> None:
        # No lock: read-modify-write can be interleaved at the await
        current = self.value
        await asyncio.sleep(0)
        self.value = current + 1

async def main() -> None:
    # --- Locked: 50 increments always produce 50 ---
    counter = SharedCounter()
    await asyncio.gather(*(counter.increment() for _ in range(50)))
    assert counter.value == 50, f"locked: expected 50, got {counter.value}"

    # --- Unlocked: 50 increments may lose updates ---
    counter.value = 0
    await asyncio.gather(*(counter.unsafe_increment() for _ in range(50)))
    # With sleep(0), CPython's default event-loop scheduling still runs
    # tasks sequentially, so the result *happens* to be 50. To observe
    # a race, each step would need variable work between read and write.
    # The key point is: the unlocked version has *no guarantee* of 50.
    assert counter.value <= 50

    print("all checks passed")

asyncio.run(main())
```

保存为 `asyncio-lock-shared-state.py` 后执行：

```bash
python3 asyncio-lock-shared-state.py
```

应输出 `all checks passed`，退出码 0。

**坑**：不要在持锁期间做慢 I/O，除非共享状态必须覆盖这段 I/O。

**检查**：临界区内是否只包含必须串行的状态读写？
