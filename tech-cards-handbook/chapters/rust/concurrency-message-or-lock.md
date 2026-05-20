# 并发共享数据优先用消息或锁

**问题**：多线程里如何安全共享状态？

**要点**：

- `std::thread` 可以启动线程。
- `Arc<T>` 让多个线程共享同一份所有权。
- `Mutex<T>` 保护可变共享状态。

**示例**：

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..4 {
    let counter = Arc::clone(&counter);
    handles.push(thread::spawn(move || {
        let mut value = counter.lock().unwrap();
        *value += 1;
    }));
}

for handle in handles {
    handle.join().unwrap();
}

assert_eq!(*counter.lock().unwrap(), 4);
```

**坑**：持有锁时做耗时 I/O，容易拖慢其他线程甚至造成死锁。

**检查**：锁保护的代码块是否尽可能短？能否改成消息传递减少共享状态？
