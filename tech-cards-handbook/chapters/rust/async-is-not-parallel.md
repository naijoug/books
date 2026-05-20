# 异步不是自动并行

**问题**：`async fn` 写了之后，任务为什么没有同时运行？

**要点**：

- `async fn` 返回 Future，只有被运行时轮询才会执行。
- `.await` 会等待当前 Future 完成。
- 真正并发需要运行时调度多个 Future。

**示例**：

```rust
async fn fetch_user(id: u64) -> String {
    format!("user-{id}")
}

async fn load_two_users() -> (String, String) {
    let left = fetch_user(1);
    let right = fetch_user(2);

    tokio::join!(left, right)
}
```

**坑**：在 async 代码里调用阻塞函数，会卡住运行时线程。阻塞 I/O 要用专门的 blocking API 或线程池。

**检查**：两个互不依赖的异步任务是否可以用 `join!` 或任务调度并发执行？
