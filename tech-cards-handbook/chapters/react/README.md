# React 技术卡片

本目录按"一张卡片一个 Markdown 文件"维护，共 41 张。文件名使用英文 `kebab-case`。

代码块验证:在 `books` 仓库根目录运行 `python3 scripts/verify_react_cards.py`,脚本会抽取本章 `ts`/`tsx`/`typescript` 代码块,用 TypeScript strict 模式和轻量 React 类型 shim 做批量检查。

## 请求与缓存阅读线

第 11-20 张卡片组成一条数据读取链路：先用“旧请求不能覆盖更新状态”处理竞态，再用 `AbortController` 取消已经失去意义的读取；网络失败时，先让自动重试有最大次数和退避，再把最后的恢复权交给用户手动重试；进入缓存层后，依次检查去重、写后失效、key 边界、TTL/版本号和 stale-while-revalidate，最后用搜索防抖把输入态和缓存 key 分开。

阅读这组卡片时，可以按同一个检查顺序审查项目代码：请求是否会被新条件淘汰、失败是否有边界、缓存是否知道“同一个读取”和“该失效的读取”分别是什么、旧数据是否能在后台刷新时保持界面稳定。这样比单独记 API 更容易发现真实产品里的数据一致性问题。

## Hook 与并发阅读线

第 1、9、10、25、36-41 张卡片可以组成一条 Hook 与并发安全阅读线：先理解 effect 只负责同步外部系统，并且必须能在 Strict Mode 的额外 setup → cleanup → setup 中正确恢复；再用 `useDeferredValue` 和 `startTransition` 区分紧急与非紧急更新；遇到复杂交互时，用 `useActionState`、`useFormStatus`、`useOptimistic` 管住提交与乐观视图；最后用 `useId`、`useSyncExternalStore` 和 Strict Mode 检查 SSR 一致性、外部 store 快照和副作用幂等性。

审查这组卡片时，可以按三问推进：这个 Hook 解决的是渲染身份、更新优先级、外部同步还是提交状态；它是否要求调用顺序、快照引用或 cleanup 保持稳定；开发环境多执行一次时，是否会暴露真实的重复订阅、重复请求或不可回滚写入。这样能把“会用 Hook”升级成“知道 Hook 的约束边界”。

| 卡片 | 文件 |
|---|---|
| React effect 同步外部系统,不处理普通计算 | [`react-effect-syncs-external-systems.md`](react-effect-syncs-external-systems.md) |
| `useMemo` 不是性能按钮 | [`usememo-is-not-performance-button.md`](usememo-is-not-performance-button.md) |
| `useCallback` 稳定的是函数身份,不是函数执行 | [`usecallback-stabilizes-callback-identity.md`](usecallback-stabilizes-callback-identity.md) |
| `memo` 的收益来自稳定 props,不是无脑包裹 | [`memo-needs-stable-props.md`](memo-needs-stable-props.md) |
| Profiler 先测量,再做性能优化 | [`profiler-measures-before-optimizing.md`](profiler-measures-before-optimizing.md) |
| 虚拟列表只渲染可见窗口,不渲染整页数据 | [`virtual-list-renders-visible-window.md`](virtual-list-renders-visible-window.md) |
| 分页负责数据边界,虚拟列表负责渲染窗口 | [`pagination-feeds-virtual-list.md`](pagination-feeds-virtual-list.md) |
| 筛选或排序变化时重置列表状态 | [`filter-sort-reset-list-state.md`](filter-sort-reset-list-state.md) |
| `useDeferredValue` 让输入保持响应,不阻塞在重列表上 | [`usedeferredvalue-keeps-input-responsive.md`](usedeferredvalue-keeps-input-responsive.md) |
| `startTransition` 标记非紧急更新,让输入和导航先响应 | [`starttransition-marks-non-urgent-updates.md`](starttransition-marks-non-urgent-updates.md) |
| 旧请求不能覆盖更新状态 | [`stale-request-must-not-overwrite-newer-state.md`](stale-request-must-not-overwrite-newer-state.md) |
| `AbortController` 取消过期读取，别让无用请求继续占资源 | [`abortcontroller-cancels-obsolete-reads.md`](abortcontroller-cancels-obsolete-reads.md) |
| 请求重试要有边界和退避 | [`request-retry-uses-bounded-backoff.md`](request-retry-uses-bounded-backoff.md) |
| 手动重试把错误恢复交还给用户 | [`manual-retry-separates-error-recovery-from-auto-retry.md`](manual-retry-separates-error-recovery-from-auto-retry.md) |
| 请求缓存去重相同读取 | [`request-cache-dedupes-identical-reads.md`](request-cache-dedupes-identical-reads.md) |
| 写操作成功后要失效相关缓存 | [`cache-invalidation-after-mutation.md`](cache-invalidation-after-mutation.md) |
| 缓存 key 设计决定失效边界 | [`cache-key-designs-invalidation-boundaries.md`](cache-key-designs-invalidation-boundaries.md) |
| 缓存过期要有 TTL 或版本号 | [`cache-ttl-version-expiration.md`](cache-ttl-version-expiration.md) |
| Stale-while-revalidate 保持缓存 UI，同时后台刷新 | [`stale-while-revalidate-keeps-cached-ui.md`](stale-while-revalidate-keeps-cached-ui.md) |
| 搜索请求防抖要分开输入值和缓存 key | [`search-debounce-separates-input-and-cache-key.md`](search-debounce-separates-input-and-cache-key.md) |
| 骨架屏要区分首屏加载和加载更多 | [`skeleton-screen-distinguishes-first-load-and-more.md`](skeleton-screen-distinguishes-first-load-and-more.md) |
| 表单状态优先靠近输入 | [`form-state-near-input.md`](form-state-near-input.md) |
| 列表 key 使用稳定身份,不使用索引 | [`stable-list-key-not-index.md`](stable-list-key-not-index.md) |
| `useState` 更新依赖旧值时用函数式更新 | [`usestate-functional-update.md`](usestate-functional-update.md) |
| Effect 必须清理订阅、定时器和请求 | [`effect-cleanup-subscriptions-timers-requests.md`](effect-cleanup-subscriptions-timers-requests.md) |
| `useRef` 保存可变值但不触发重渲染 | [`useref-mutable-value-no-render.md`](useref-mutable-value-no-render.md) |
| 自定义 Hook 用来复用状态逻辑 | [`custom-hook-reuse-state-logic.md`](custom-hook-reuse-state-logic.md) |
| Error Boundary 捕获渲染失败,不捕获事件失败 | [`error-boundary-catches-render-failures.md`](error-boundary-catches-render-failures.md) |
| Suspense 处理等待,Error Boundary 处理失败 | [`suspense-waits-error-boundary-fails.md`](suspense-waits-error-boundary-fails.md) |
| `React.lazy` 优先切路由和重模块,不要随机拆小组件 | [`react-lazy-splits-routes-not-random-widgets.md`](react-lazy-splits-routes-not-random-widgets.md) |
| Error Boundary 的重试需要重置失败子树 | [`error-boundary-reset-retry.md`](error-boundary-reset-retry.md) |
| Context 拆分状态和动作,避免全树重渲染 | [`context-split-state-and-actions.md`](context-split-state-and-actions.md) |
| 异步状态用联合类型表达,不用多个布尔值 | [`async-state-discriminated-union.md`](async-state-discriminated-union.md) |
| 乐观更新必须有回滚路径 | [`optimistic-update-with-rollback.md`](optimistic-update-with-rollback.md) |
| `useActionState` 把表单提交状态收拢到 action | [`useactionstate-keeps-form-submission-state.md`](useactionstate-keeps-form-submission-state.md) |
| `useFormStatus` 只放在表单内部读取提交状态 | [`useformstatus-belongs-inside-form.md`](useformstatus-belongs-inside-form.md) |
| `useOptimistic` 只覆盖过渡中的乐观视图 | [`useoptimistic-overlays-transient-state.md`](useoptimistic-overlays-transient-state.md) |
| 加载更多时必须有并发锁，防止重复请求 | [`load-more-lock-prevents-duplicate-requests.md`](load-more-lock-prevents-duplicate-requests.md) |
| `useId` 生成跨 SSR 与 CSR 稳定的唯一 ID | [`useid-generates-stable-ssr-csr-ids.md`](useid-generates-stable-ssr-csr-ids.md) |
| `useSyncExternalStore` 订阅外部状态源 | [`usesyncexternalstore-subscribes-external-state.md`](usesyncexternalstore-subscribes-external-state.md) |
| Strict Mode 双次调用暴露副作用 | [`strict-mode-double-invokes-effects.md`](strict-mode-double-invokes-effects.md) |
