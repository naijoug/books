# 并发共享数据优先用消息或锁

**问题**：多线程里如何安全共享状态？

**要点**：

- `std::thread` 可以启动线程；跨线程移动的数据必须满足 `Send`。
- 能把数据所有权交给某个线程时，优先用消息传递（`std::sync::mpsc`），避免多个线程同时改同一份状态。
- 确实需要共享可变状态时，用 `Arc<Mutex<T>>`：`Arc<T>` 共享所有权，`Mutex<T>` 保护临界区。
- 锁只包住最小必要代码，先把数据取出来，再做格式化、I/O 或耗时计算。

**示例**：

```rust
use std::sync::{mpsc, Arc, Mutex};
use std::thread;

#[derive(Debug, Clone, PartialEq, Eq)]
struct JobDone {
    worker_id: usize,
    units: u32,
}

fn collect_by_message() -> Vec<JobDone> {
    let (tx, rx) = mpsc::channel();
    let mut handles = Vec::new();

    for worker_id in 0..4 {
        let tx = tx.clone();
        handles.push(thread::spawn(move || {
            let units = (worker_id as u32 + 1) * 10;
            tx.send(JobDone { worker_id, units }).unwrap();
        }));
    }

    // 关闭主线程持有的发送端，否则 rx 迭代器会一直等待新消息。
    drop(tx);

    let mut reports: Vec<JobDone> = rx.into_iter().collect();

    for handle in handles {
        handle.join().unwrap();
    }

    reports.sort_by_key(|report| report.worker_id);
    reports
}

fn count_with_lock() -> u32 {
    let counter = Arc::new(Mutex::new(0_u32));
    let mut handles = Vec::new();

    for _ in 0..4 {
        let counter = Arc::clone(&counter);
        handles.push(thread::spawn(move || {
            for _ in 0..25 {
                // 临界区只负责修改共享计数，不在锁内打印或做耗时工作。
                let mut value = counter.lock().unwrap();
                *value += 1;
            }
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let value = counter.lock().unwrap();
    *value
}

fn main() {
    let reports = collect_by_message();
    assert_eq!(reports.len(), 4);
    assert_eq!(reports[0], JobDone { worker_id: 0, units: 10 });
    assert_eq!(reports.iter().map(|report| report.units).sum::<u32>(), 100);

    let total = count_with_lock();
    assert_eq!(total, 100);

    println!("message reports: {:?}", reports);
    println!("locked counter total: {total}");
    println!("concurrency demo done");
}
```

**坑**：持有锁时做耗时 I/O，容易拖慢其他线程甚至造成死锁；忘记 `drop(tx)` 时，接收端迭代器会一直等待仍然存在的发送端。

**检查**：

- 数据是否可以通过消息“交给一个拥有者处理”？可以就先用 channel。
- 如果必须共享可变状态，锁保护的代码块是否尽可能短？
- 每个 `thread::spawn` 之后是否有清晰的 `join` 或生命周期管理？
