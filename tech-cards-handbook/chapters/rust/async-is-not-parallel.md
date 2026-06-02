# 异步不是自动并行

**问题**：`async fn` 写了之后，任务为什么没有同时运行？

**要点**：

- `async fn` 返回 Future；调用它只是在创建状态机，只有被执行器轮询（poll）才会真正向前跑。
- `.await` 会等待当前 Future 完成；如果先 `await left` 再 `await right`，两个任务就是顺序推进。
- 真正并发需要执行器在多个 Future 之间交替轮询；并发不等于多线程并行，是否并行取决于运行时和任务是否被派到不同线程。

**示例**：

```rust
use std::cell::RefCell;
use std::future::Future;
use std::pin::Pin;
use std::rc::Rc;
use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};

type Log = Rc<RefCell<Vec<String>>>;

struct YieldOnce {
    label: &'static str,
    yielded: bool,
    log: Log,
}

impl Future for YieldOnce {
    type Output = ();

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        self.log.borrow_mut().push(format!("poll {}", self.label));
        if self.yielded {
            Poll::Ready(())
        } else {
            self.yielded = true;
            cx.waker().wake_by_ref();
            Poll::Pending
        }
    }
}

async fn fetch_user(id: u64, log: Log) -> String {
    log.borrow_mut().push(format!("start user-{id}"));
    YieldOnce {
        label: if id == 1 { "user-1" } else { "user-2" },
        yielded: false,
        log: Rc::clone(&log),
    }
    .await;
    log.borrow_mut().push(format!("done user-{id}"));
    format!("user-{id}")
}

async fn load_sequential(log: Log) -> (String, String) {
    let left = fetch_user(1, Rc::clone(&log)).await;
    let right = fetch_user(2, Rc::clone(&log)).await;
    (left, right)
}

fn join_two<F1, F2>(left: F1, right: F2) -> (String, String)
where
    F1: Future<Output = String>,
    F2: Future<Output = String>,
{
    let waker = noop_waker();
    let mut cx = Context::from_waker(&waker);
    let mut left = Box::pin(left);
    let mut right = Box::pin(right);
    let mut left_out = None;
    let mut right_out = None;

    loop {
        if left_out.is_none() {
            if let Poll::Ready(value) = left.as_mut().poll(&mut cx) {
                left_out = Some(value);
            }
        }
        if right_out.is_none() {
            if let Poll::Ready(value) = right.as_mut().poll(&mut cx) {
                right_out = Some(value);
            }
        }
        if let (Some(left), Some(right)) = (left_out.take(), right_out.take()) {
            return (left, right);
        }
    }
}

fn block_on<F: Future>(future: F) -> F::Output {
    let waker = noop_waker();
    let mut cx = Context::from_waker(&waker);
    let mut future = Box::pin(future);

    loop {
        if let Poll::Ready(value) = future.as_mut().poll(&mut cx) {
            return value;
        }
    }
}

fn noop_waker() -> Waker {
    unsafe fn clone(_: *const ()) -> RawWaker {
        raw_waker()
    }
    unsafe fn wake(_: *const ()) {}
    unsafe fn wake_by_ref(_: *const ()) {}
    unsafe fn drop(_: *const ()) {}

    fn raw_waker() -> RawWaker {
        RawWaker::new(
            std::ptr::null(),
            &RawWakerVTable::new(clone, wake, wake_by_ref, drop),
        )
    }

    unsafe { Waker::from_raw(raw_waker()) }
}

fn main() {
    let idle_log = Rc::new(RefCell::new(Vec::new()));
    let _created_but_not_polled = fetch_user(99, Rc::clone(&idle_log));
    assert!(idle_log.borrow().is_empty());

    let sequential_log = Rc::new(RefCell::new(Vec::new()));
    let sequential = block_on(load_sequential(Rc::clone(&sequential_log)));
    assert_eq!(sequential, ("user-1".to_string(), "user-2".to_string()));

    let concurrent_log = Rc::new(RefCell::new(Vec::new()));
    let concurrent = join_two(
        fetch_user(1, Rc::clone(&concurrent_log)),
        fetch_user(2, Rc::clone(&concurrent_log)),
    );
    assert_eq!(concurrent, ("user-1".to_string(), "user-2".to_string()));

    println!("sequential poll order: {:?}", sequential_log.borrow());
    println!("concurrent poll order: {:?}", concurrent_log.borrow());
    println!("async demo done");
}
```

**观察**：

- `_created_but_not_polled` 没有被执行，日志为空；Future 只是“待执行的计算”。
- `load_sequential` 先把 `user-1` 等完，再开始 `user-2`。
- `join_two` 模拟一个最小执行器，在两个 Future 之间轮询；它展示的是单线程并发，而不是 CPU 并行。

**坑**：在 async 代码里调用阻塞函数，会卡住运行时线程。阻塞 I/O 要用专门的 blocking API 或线程池。

**检查**：两个互不依赖的异步任务是否可以用 `join!`、`select!` 或任务调度并发执行？是否有阻塞调用混在 async 路径里？
