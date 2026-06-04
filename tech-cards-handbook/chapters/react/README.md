# React 技术卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 19 张。文件名使用英文 `kebab-case`。

代码块验证：在 `books` 仓库根目录运行 `python3 scripts/verify_react_cards.py`，脚本会抽取本章 `ts`/`tsx`/`typescript` 代码块，用 TypeScript strict 模式和轻量 React 类型 shim 做批量检查。

| 卡片 | 文件 |
|---|---|
| React effect 同步外部系统，不处理普通计算 | [`react-effect-syncs-external-systems.md`](react-effect-syncs-external-systems.md) |
| `useMemo` 不是性能按钮 | [`usememo-is-not-performance-button.md`](usememo-is-not-performance-button.md) |
| `useCallback` 稳定的是函数身份，不是函数执行 | [`usecallback-stabilizes-callback-identity.md`](usecallback-stabilizes-callback-identity.md) |
| 表单状态优先靠近输入 | [`form-state-near-input.md`](form-state-near-input.md) |
| 列表 key 使用稳定身份，不使用索引 | [`stable-list-key-not-index.md`](stable-list-key-not-index.md) |
| `useState` 更新依赖旧值时用函数式更新 | [`usestate-functional-update.md`](usestate-functional-update.md) |
| Effect 必须清理订阅、定时器和请求 | [`effect-cleanup-subscriptions-timers-requests.md`](effect-cleanup-subscriptions-timers-requests.md) |
| `useRef` 保存可变值但不触发重渲染 | [`useref-mutable-value-no-render.md`](useref-mutable-value-no-render.md) |
| 自定义 Hook 用来复用状态逻辑 | [`custom-hook-reuse-state-logic.md`](custom-hook-reuse-state-logic.md) |
| Error Boundary 捕获渲染失败，不捕获事件失败 | [`error-boundary-catches-render-failures.md`](error-boundary-catches-render-failures.md) |
| Suspense 处理等待，Error Boundary 处理失败 | [`suspense-waits-error-boundary-fails.md`](suspense-waits-error-boundary-fails.md) |
| `React.lazy` 优先切路由和重模块，不要随机拆小组件 | [`react-lazy-splits-routes-not-random-widgets.md`](react-lazy-splits-routes-not-random-widgets.md) |
| Error Boundary 的重试需要重置失败子树 | [`error-boundary-reset-retry.md`](error-boundary-reset-retry.md) |
| Context 拆分状态和动作，避免全树重渲染 | [`context-split-state-and-actions.md`](context-split-state-and-actions.md) |
| 异步状态用联合类型表达，不用多个布尔值 | [`async-state-discriminated-union.md`](async-state-discriminated-union.md) |
| 乐观更新必须有回滚路径 | [`optimistic-update-with-rollback.md`](optimistic-update-with-rollback.md) |
| `useActionState` 把表单提交状态收拢到 action | [`useactionstate-keeps-form-submission-state.md`](useactionstate-keeps-form-submission-state.md) |
| `useFormStatus` 只放在表单内部读取提交状态 | [`useformstatus-belongs-inside-form.md`](useformstatus-belongs-inside-form.md) |
| `useOptimistic` 只覆盖过渡中的乐观视图 | [`useoptimistic-overlays-transient-state.md`](useoptimistic-overlays-transient-state.md) |
