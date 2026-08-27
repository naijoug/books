# 测试 Fixture 失败消息也是交接材料

**问题**：Agent 给测试 fixture 里的 `unwrap()` 换成 `expect()`，看起来只是文案小修；但如果失败消息不能帮助下一轮区分“fixture 准备失败、外部命令启动失败、被测逻辑失败、清理失败”，这类改动就只是 diff 噪音。怎样把测试失败消息写成可交接证据，而不是把裸 panic 换成另一种裸 panic？

**要点**：

- 先按 fixture 生命周期分段：准备目录、写入输入、启动外部命令、调用被测函数、清理现场；每段失败消息都写清“动作 + 语义对象”。
- 只改测试失败信息，不顺手改生产错误处理、断言顺序、返回类型或锁语义；否则这轮已经从诊断性小修变成行为变更。
- 外部命令测试要分清“命令无法启动”和“命令启动后 exit 失败”；后者的断言消息至少带上子命令参数、stdout、stderr。
- 清理失败不要静默吞掉：如果清理是测试契约，用 `expect("remove ... fixture root")`；如果是 best-effort，就显式说明为什么不阻断。
- 验证以聚焦测试为主：先跑涉及模块的 formatter、目标测试和 `git diff --check`；只有当 fixture 依赖平台、权限或外部服务时，再升级到更大的 smoke test。
- 最终 notebook / PR 说明里记录失败语义化的边界：本轮改善的是诊断信息，不声称覆盖了新的业务行为。

**示例**：

```text
Observation:
某个 Rust 模块的测试会创建临时 repo、写入 pre-existing/task 文件并调用 git；失败时只有 `called Result::unwrap()`。

Human hypothesis before agent:
如果不改业务逻辑，只给 fixture 准备和 git 子命令失败加语义化消息，下一轮看到红灯时能先定位环境 / fixture / 断言层级。

Change:
- `create_dir_all(...).expect("create baseline git fixture root")`
- `write(...).expect("write pre-existing baseline fixture")`
- `Command::new("git").output().expect("start git command for baseline fixture")`
- `assert!(output.status.success(), "git command failed for baseline fixture: {args:?}\nstdout: ...\nstderr: ...")`

Verification:
运行 `cargo fmt --manifest-path src-tauri/Cargo.toml`、`cargo test project_git --manifest-path src-tauri/Cargo.toml`、`git diff --check -- src-tauri/src/project_git.rs`。

Handoff:
这次只提升测试失败可诊断性；若后续目标测试红灯，先按失败消息判断是 fixture 环境问题还是业务断言问题，不要直接扩大到生产重构。
```

**反例 / 修正做法**：

```text
反例：
- 把所有 `unwrap()` 机械替换成 `expect("failed")`。
- 为了消除测试里的 panic，顺手改生产 `Mutex::lock().unwrap()` 的错误处理。
- 外部命令失败只写 `assert!(status.success())`，不保留 stdout / stderr。
- 删除临时目录失败被 `_ = remove_dir_all(...)` 静默忽略。

修正：
- 先确认这些 panic 位于测试 fixture，而不是生产路径。
- 每条消息回答“哪一步、哪个对象、用于哪个测试语义”。
- 行为变化单独立任务；本轮只提交诊断性文案和对应聚焦验证。
```

**坑**：

- **把可诊断性当覆盖率**：更好的失败消息不能证明业务路径更安全；不要在报告里写成“补强测试覆盖”。
- **消息太抽象**：`expect("setup")`、`expect("ok")` 和裸 `unwrap()` 对接力几乎等价。
- **一次扫太多模块**：全局替换会扩大 review 面积，也容易混入生产路径行为变化。
- **验证命令不贴近改动**：只跑全量测试但没有目标测试，下一轮难以知道哪条证据覆盖了本轮文件。
- **忽略 dirty 边界**：在已有未接管改动的 repo 里做这类小修，必须 path-scoped stage / commit，避免把别人的测试改动混入。

**检查**：提交前逐条问：新消息是否能定位 fixture 阶段；是否没有改变生产逻辑；外部命令是否带 stdout / stderr；清理失败是否有明确策略；验证是否包含目标测试和 whitespace 检查。任一项缺失，就先补证据，不要把“更换 panic 文案”包装成已闭环的测试改进。
