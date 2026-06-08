# React 技术卡片

本目录按"一张卡片一个 Markdown 文件"维护,共 51 张。文件名使用英文 `kebab-case`。

代码块验证:在 `books` 仓库根目录运行 `python3 scripts/verify_react_cards.py`,脚本会抽取本章 `ts`/`tsx`/`typescript` 代码块,用 TypeScript strict 模式和轻量 React 类型 shim 做批量检查。

## 性能与渲染阅读线

[`Profiler 先测量`](profiler-measures-before-optimizing.md)、[`useMemo`](usememo-is-not-performance-button.md)、[`useCallback`](usecallback-stabilizes-callback-identity.md)、[`memo`](memo-needs-stable-props.md)、[`稳定 key`](stable-list-key-not-index.md)、[`分页与虚拟列表`](pagination-feeds-virtual-list.md)、[`虚拟窗口`](virtual-list-renders-visible-window.md)、[`加载更多锁`](load-more-lock-prevents-duplicate-requests.md)、[`Suspense/Error Boundary`](suspense-waits-error-boundary-fails.md)、[`React.lazy`](react-lazy-splits-routes-not-random-widgets.md) 和 [`Error Boundary 重试`](error-boundary-reset-retry.md) 可以组成一条性能与渲染阅读线:先用 Profiler 找到真实瓶颈,再决定 `useMemo`、`useCallback` 和 `memo` 是否值得引入;列表场景先分清稳定 key、分页边界、虚拟窗口和加载更多状态;重组件或重路由再用 Suspense、代码分割和 Error Boundary 重试边界控制加载、失败与恢复。这样能避免把性能优化写成"到处包 memo"或"随手 lazy 一切组件"。

审查这组卡片时,先问用户感知的问题在哪里:是输入卡顿、列表首屏慢、加载更多闪烁、路由切换白屏,还是失败后无法恢复。只有把现象、测量点和组件边界对齐,性能优化才不会变成增加复杂度的装饰。

### 性能与渲染代码审查清单

把这组卡片落到真实项目时,可以按下面顺序检查,不要先从 API 清单反推需求:

1. **先测量再优化**:是否用 Profiler 或浏览器性能面板定位具体慢组件、慢交互和重复提交,而不是凭感觉加 memo。
2. **计算缓存边界**:`useMemo` 是否包住昂贵且输入稳定的计算;是否避免把普通常量、轻量映射或副作用塞进 memo。
3. **函数身份边界**:`useCallback` 是否服务于 memo 子组件、Effect 依赖或订阅解绑;是否避免为了"依赖少"隐藏真实依赖。
4. **组件 memo 收益**:`memo` 的 props 是否稳定且渲染成本足够高;父组件频繁更新时,是否确认子组件真的会被跳过。
5. **列表身份稳定**:列表 key 是否来自业务 ID;新增、删除、排序、筛选后,输入焦点、展开态和本地状态是否不会错位。
6. **数据边界清楚**:分页负责服务端数据窗口,虚拟列表负责浏览器渲染窗口;是否没有用虚拟列表掩盖一次性拉取过量数据的问题。
7. **加载状态分层**:首屏、分页加载更多、后台刷新和错误恢复是否有不同 UI;是否避免每次追加数据都把整页替换成全屏 loading。
8. **代码分割颗粒度**:lazy 是否优先切路由、富编辑器、图表等重模块;是否避免把小组件切得过碎导致请求瀑布。
9. **等待与失败边界**:Suspense fallback 是否靠近真正等待的区域;Error Boundary 重试是否能重置失败子树,而不是只能刷新整页。
10. **优化可回滚**:每个性能优化是否有可复测指标或注释说明;当 props 稳定性被破坏时,是否容易删除或调整,而不是形成不可解释的包裹层。

## 请求与缓存阅读线

[`旧请求不能覆盖更新状态`](stale-request-must-not-overwrite-newer-state.md)、[`AbortController 取消过期读取`](abortcontroller-cancels-obsolete-reads.md)、[`有边界的请求重试`](request-retry-uses-bounded-backoff.md)、[`手动重试`](manual-retry-separates-error-recovery-from-auto-retry.md)、[`请求缓存去重`](request-cache-dedupes-identical-reads.md)、[`写后失效`](cache-invalidation-after-mutation.md)、[`缓存 key 设计`](cache-key-designs-invalidation-boundaries.md)、[`TTL/版本号`](cache-ttl-version-expiration.md)、[`stale-while-revalidate`](stale-while-revalidate-keeps-cached-ui.md) 和 [`搜索防抖`](search-debounce-separates-input-and-cache-key.md) 组成一条数据读取链路:先处理竞态,再取消已经失去意义的读取;网络失败时,先让自动重试有最大次数和退避,再把最后的恢复权交给用户手动重试;进入缓存层后,依次检查去重、写后失效、key 边界、TTL/版本号和 stale-while-revalidate,最后用搜索防抖把输入态和缓存 key 分开。

阅读这组卡片时，可以按同一个检查顺序审查项目代码：请求是否会被新条件淘汰、失败是否有边界、缓存是否知道"同一个读取"和"该失效的读取"分别是什么、旧数据是否能在后台刷新时保持界面稳定。这样比单独记 API 更容易发现真实产品里的数据一致性问题。

### 请求与缓存代码审查清单

把这组卡片落到真实项目时，可以按下面顺序检查，而不是只看某个请求库是否"接上了"：

1. **竞态淘汰**：条件变化时（切换页码、修改筛选、输入搜索词），上一次请求的结果是否被安全丢弃，而不是覆盖更新状态。
2. **请求取消**：失去意义的读取是否通过 `AbortController` 取消，而不是让它在后台静默完成并浪费连接。
3. **自动重试边界**：失败重试是否有最大次数和指数退避；是否避免在服务端明确拒绝（403、404、422）时仍然盲目重试。
4. **手动重试兜底**：自动重试耗尽后，是否把恢复权交还给用户（"点击重试"），而不是自动跳转错误页或静默放弃。
5. **请求去重**：组件树中多处发起的相同读取（相同 URL + 相同参数）是否被缓存层合并为一次网络请求。
6. **写后失效**：增删改成功后，相关的列表、详情和聚合缓存是否被显式失效或更新，而不是依赖 TTL 自然过期。
7. **缓存 key 设计**：缓存 key 是否包含所有影响数据的参数（筛选条件、分页、排序、用户身份）；key 变化时旧缓存是否不再命中。
8. **过期与刷新**：缓存是否有 TTL 或版本号机制；`stale-while-revalidate` 是否让旧数据在后台刷新期间继续服务界面，而不是返回空白或闪烁。
9. **搜索防抖分离**：用户输入值和实际缓存 key 是否分开维护；防抖是否作用于请求触发，而不是延迟输入框的显示值。
10. **加载状态区分**：首屏加载是否显示骨架屏或空白占位，加载更多是否显示底部 spinner 而不是替换已有列表。

## Hook 与并发阅读线

[`Effect 同步外部系统`](react-effect-syncs-external-systems.md)、[`useDeferredValue`](usedeferredvalue-keeps-input-responsive.md)、[`startTransition`](starttransition-marks-non-urgent-updates.md)、[`表单 action contract`](server-action-result-contract-keeps-form-recoverable.md)、[`useActionState`](useactionstate-keeps-form-submission-state.md)、[`useFormStatus`](useformstatus-belongs-inside-form.md)、[`useOptimistic`](useoptimistic-overlays-transient-state.md)、[`useId`](useid-generates-stable-ssr-csr-ids.md)、[`hydration 稳定输入`](hydration-mismatch-stable-inputs.md)、[`浏览器 API 客户端读取`](browser-api-reads-belong-after-client-mount.md)、[`客户端个性化外壳`](client-personalization-needs-stable-shell.md)、[`SSR 个性化首屏占位策略`](ssr-personalization-placeholder-strategy.md)、[`useSyncExternalStore`](usesyncexternalstore-subscribes-external-state.md)、[`Strict Mode`](strict-mode-double-invokes-effects.md)、[`useReducer`](usereducer-centralizes-complex-state-transitions.md) 和 [`状态机`](state-machine-eliminates-impossible-ui-states.md) 可以组成一条 Hook 与并发安全阅读线:先理解 effect 只负责同步外部系统,并且必须能在 Strict Mode 的额外 setup → cleanup → setup 中正确恢复;再用 `useDeferredValue` 和 `startTransition` 区分紧急与非紧急更新;遇到复杂交互时,用提交类 Hook 管住提交与乐观视图;最后检查 SSR 一致性、个性化外壳和占位策略、外部 store 快照、副作用幂等性、复杂状态转移边界和 UI 不可能状态。

审查这组卡片时,可以按三问推进:这个 Hook 解决的是渲染身份、更新优先级、外部同步还是提交状态;它是否要求调用顺序、快照引用或 cleanup 保持稳定;开发环境多执行一次时,是否会暴露真实的重复订阅、重复请求或不可回滚写入。这样能把"会用 Hook"升级成"知道 Hook 的约束边界"。

### Hook 与并发代码审查清单

把这组卡片落到真实项目时,可以按下面顺序检查,不要把 Hook 当成"性能优化装饰器"或"状态库替代品":

1. **外部同步边界**:Effect 是否只同步订阅、计时器、DOM、网络等外部系统;普通计算是否仍留在渲染或 memo 化计算里。
2. **清理可逆性**:每个 Effect 的 setup 是否都有对称 cleanup;Strict Mode 额外 setup → cleanup → setup 后,订阅数、定时器和请求是否不会翻倍。
3. **渲染身份稳定**:`useMemo`、`useCallback`、`memo` 是否服务于已测量的稳定 props 或昂贵计算,而不是为了"看起来高级"层层包裹。
4. **更新优先级**:输入、点击、导航等紧急更新是否先响应;搜索结果、重列表和路由切换等非紧急更新是否用 `useDeferredValue` 或 `startTransition` 降级。
5. **提交状态归属**:`useActionState`、`useFormStatus`、`useOptimistic` 是否只管理提交过渡中的状态,而不是把长期业务数据藏在临时乐观层里。
6. **SSR/CSR 身份一致**:需要稳定 ID 的表单控件、label、aria 属性是否使用 `useId`;是否避免用随机数或时间戳制造 hydration 不一致。
7. **外部 store 快照**:`useSyncExternalStore` 的快照引用是否稳定;订阅函数是否不会在每次渲染时制造新的无效订阅。
8. **复杂转移可测试**:事件分支增多时,是否把状态转移收敛到 `useReducer` 或显式状态机,并让 reducer 保持纯函数、可单测。
9. **并发下的幂等性**:同一用户意图在重渲染、重试、并发中断后是否仍只产生一次真实副作用;不可回滚写入是否有额外保护。

### SSR 与 hydration 代码审查清单

把 `useId`、hydration 稳定输入、客户端挂载后读取浏览器 API、客户端个性化外壳和 SSR 个性化首屏占位策略这五张卡片落到 SSR/预渲染项目时,可以把审查重点从"消掉 warning"前移到"首屏输入是否稳定":

1. **首屏数据来源一致**:服务端渲染和客户端第一次渲染是否读取同一份业务数据、同一套 feature flag 和同一份 i18n 文案;是否避免客户端首渲直接读取 `Date.now()`、随机数或浏览器专属状态。
2. **ID 与无障碍关系稳定**:表单控件、label、aria-describedby、错误提示等跨节点关系是否用 `useId` 或服务端传入的稳定 ID;列表项是否仍使用业务 ID 做 key。
3. **浏览器能力延后读取**:`window`、`document`、`localStorage`、`matchMedia`、视口尺寸和时区等只存在于浏览器的输入,是否放到客户端挂载后的 Effect 或专门的 client-only 边界里读取。
4. **首屏占位可接受**:需要等客户端确认的主题、布局、权限或个性化内容,是否有稳定占位或渐进增强策略;是否避免为了读取浏览器状态让整块首屏变空白。
5. **差异有意而可解释**:确实允许 SSR 与 CSR 不同的区域,是否用明确边界、注释或框架提供的 suppression 机制说明原因;是否避免把 suppression 当成通用修复。
6. **回归可复现**:是否能在关闭缓存、不同语言/时区、深色模式、窄屏和无登录态下复测 hydration;是否把曾经出错的输入源写进测试或审查清单。

## 状态管理阅读线

[`useState 函数式更新`](usestate-functional-update.md)、[`异步状态联合类型`](async-state-discriminated-union.md)、[`Context 拆分状态和动作`](context-split-state-and-actions.md)、[`useReducer`](usereducer-centralizes-complex-state-transitions.md) 和 [`状态机`](state-machine-eliminates-impossible-ui-states.md) 可以组成一条从局部状态到流程状态的建模路径:简单计数或切换先用 `useState` 的函数式更新避免闭包旧值;异步读取和提交结果用联合类型表达互斥状态;跨层共享时先拆分 Context 的 state 与 actions;当事件分支变多,再把状态转移收拢到 `useReducer`;最后用显式状态机检查步骤流里的合法转移和不可能状态。

审查这组卡片时,不要先问"该用哪个库",而要先画出状态表:有哪些状态、哪些事件会改变它、哪些状态组合不应该出现、异步结果回来时是否仍属于当前状态。只要状态表能写清楚,React 代码通常会自然落在 `useState`、`useReducer`、Context 或外部 store 的合适边界上。

### 状态管理代码审查清单

把这组卡片落到真实项目时,可以先审状态模型,再审 API 选择:

1. **状态归属**:只被一个输入或组件消费的状态是否保留在局部;跨组件共享前,是否确认真的需要共享而不是 props 下传。
2. **旧值更新**:依赖前一状态计算新状态时,是否使用函数式更新,避免事件闭包或批处理导致读到旧值。
3. **互斥状态**:加载中、成功、空结果、字段错误、系统错误等是否用联合类型表达;是否避免多个布尔值拼出 impossible state。
4. **事件表完整**:是否列清楚哪些事件能改变状态;每个事件在当前状态下是允许、忽略还是报错,而不是让任意分支随时写状态。
5. **Context 边界**:Context 是否拆分 state 与 actions;高频变化的数据是否没有放进会导致全树重渲染的全局 Provider。
6. **Reducer 纯度**:`useReducer` 是否只计算下一状态;网络请求、日志、导航等副作用是否放在事件处理或 Effect 边界。
7. **状态机合法性**:多步骤流程是否有显式状态机或转移表;取消、返回、重试、超时等边缘事件是否都有合法去向。
8. **异步回包归属**:请求或提交结果回来时,是否校验它仍属于当前状态/版本;过期结果是否不会覆盖用户后续操作。
9. **可测试性**:核心状态转移是否能用输入状态 + 事件 → 输出状态单独测试;复杂 UI 是否不需要靠手点流程才能证明正确。

## 表单与提交阅读线

[`表单状态靠近输入`](form-state-near-input.md)、[`函数式更新`](usestate-functional-update.md)、[`异步状态联合类型`](async-state-discriminated-union.md)、[`字段错误归属`](field-errors-belong-to-fields.md)、[`pending 锁与幂等键`](form-submit-idempotency-key-prevents-duplicate-writes.md)、[`action 返回 contract`](server-action-result-contract-keeps-form-recoverable.md)、[`useActionState`](useactionstate-keeps-form-submission-state.md)、[`useFormStatus`](useformstatus-belongs-inside-form.md)、[`useOptimistic`](useoptimistic-overlays-transient-state.md) 和 [`成功后一致性`](form-success-invalidates-cache-before-reset.md) 可以组成一条表单交互链路:先把输入值和字段状态放在离输入最近的位置,再把字段级错误、全局错误和服务端校验结果分开归属;提交时用提交类 Hook 收拢请求结果、显示 pending、覆盖提交过渡中的临时视图;遇到真实写操作,再用 pending 锁和幂等键把重复点击、网络重试和服务端重复写入一起关住;服务端 action 的返回结构则要把字段错误、表单级错误和成功消息做成可恢复 contract;成功后再按"缓存失效/本地合并、用户反馈、表单重置"的顺序收尾。这样能避免"一个全局 loading 管所有字段""所有错误塞进一段文案""只靠禁用按钮防重复提交""可恢复校验失败被当成系统异常"和"成功清空输入却留下旧列表"的粗糙实现。

审查表单代码时,可以按一次真实提交流程走查:用户改动字段时是否只清理相关错误;重复点击提交是否被 pending 状态挡住;服务端返回字段错误后是否能正确回填到对应输入;乐观视图失败时是否能回滚;需要修改输入才能恢复的错误,是否没有被误做成无意义的"重试"按钮;响应丢失后再次点击是否复用同一个幂等键,而不是创建第二条业务记录。

### 表单提交代码审查清单

把这组卡片落到真实项目时,可以按下面顺序检查,而不是只看某个 Hook 是否"用上了":

1. **字段归属**:输入值、touched、dirty、字段错误是否靠近字段维护;修改单个字段时,是否只清掉这个字段的旧错误。
2. **状态模型**:提交结果是否用互斥状态表达,例如 idle、submitting、success、field_error、form_error;是否避免多个布尔值拼出不可能状态。
3. **提交入口**:提交按钮是否依赖表单内部的 pending 状态;键盘提交、双击按钮和脚本触发是否走同一个 action,而不是绕过锁。
4. **服务端 contract**:字段错误、表单级错误、成功消息和不可恢复异常是否分开返回;可恢复校验失败是否没有被扔进 Error Boundary。
5. **重复写入**:真实写操作是否有幂等键;网络失败后的重试是否复用同一个 key;用户修改关键字段后是否刷新 key。
6. **乐观视图**:只在用户已经表达明确提交意图后显示乐观结果;失败时是否能回滚到服务端确认前的状态。
7. **写后一致性**:提交成功后,相关列表、详情、计数和本地缓存是否失效或更新;重置表单前是否先确认成功状态已经被用户看见或被业务流程消费。
8. **可观测性**:服务端是否记录用户、动作、幂等键、请求摘要和结果;排查重复提交时能否判断是前端重复触发、网络重试还是服务端去重失败。

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
| `AbortController` 取消过期读取,别让无用请求继续占资源 | [`abortcontroller-cancels-obsolete-reads.md`](abortcontroller-cancels-obsolete-reads.md) |
| 请求重试要有边界和退避 | [`request-retry-uses-bounded-backoff.md`](request-retry-uses-bounded-backoff.md) |
| 手动重试把错误恢复交还给用户 | [`manual-retry-separates-error-recovery-from-auto-retry.md`](manual-retry-separates-error-recovery-from-auto-retry.md) |
| 请求缓存去重相同读取 | [`request-cache-dedupes-identical-reads.md`](request-cache-dedupes-identical-reads.md) |
| 写操作成功后要失效相关缓存 | [`cache-invalidation-after-mutation.md`](cache-invalidation-after-mutation.md) |
| 缓存 key 设计决定失效边界 | [`cache-key-designs-invalidation-boundaries.md`](cache-key-designs-invalidation-boundaries.md) |
| 缓存过期要有 TTL 或版本号 | [`cache-ttl-version-expiration.md`](cache-ttl-version-expiration.md) |
| Stale-while-revalidate 保持缓存 UI,同时后台刷新 | [`stale-while-revalidate-keeps-cached-ui.md`](stale-while-revalidate-keeps-cached-ui.md) |
| 搜索请求防抖要分开输入值和缓存 key | [`search-debounce-separates-input-and-cache-key.md`](search-debounce-separates-input-and-cache-key.md) |
| 骨架屏要区分首屏加载和加载更多 | [`skeleton-screen-distinguishes-first-load-and-more.md`](skeleton-screen-distinguishes-first-load-and-more.md) |
| 表单状态优先靠近输入 | [`form-state-near-input.md`](form-state-near-input.md) |
| 表单校验错误按字段归属 | [`field-errors-belong-to-fields.md`](field-errors-belong-to-fields.md) |
| 表单提交用 pending 锁和幂等键防重复写入 | [`form-submit-idempotency-key-prevents-duplicate-writes.md`](form-submit-idempotency-key-prevents-duplicate-writes.md) |
| 表单 action 返回结构要让错误可恢复 | [`server-action-result-contract-keeps-form-recoverable.md`](server-action-result-contract-keeps-form-recoverable.md) |
| 表单成功后先处理一致性,再重置输入 | [`form-success-invalidates-cache-before-reset.md`](form-success-invalidates-cache-before-reset.md) |
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
| 加载更多时必须有并发锁,防止重复请求 | [`load-more-lock-prevents-duplicate-requests.md`](load-more-lock-prevents-duplicate-requests.md) |
| `useId` 生成跨 SSR 与 CSR 稳定的唯一 ID | [`useid-generates-stable-ssr-csr-ids.md`](useid-generates-stable-ssr-csr-ids.md) |
| Hydration 不一致要从稳定输入源治理 | [`hydration-mismatch-stable-inputs.md`](hydration-mismatch-stable-inputs.md) |
| 浏览器 API 读取放到客户端挂载之后 | [`browser-api-reads-belong-after-client-mount.md`](browser-api-reads-belong-after-client-mount.md) |
| 客户端个性化首屏要先有稳定外壳 | [`client-personalization-needs-stable-shell.md`](client-personalization-needs-stable-shell.md) |
| SSR 个性化首屏要有渐进占位策略 | [`ssr-personalization-placeholder-strategy.md`](ssr-personalization-placeholder-strategy.md) |
| `useSyncExternalStore` 订阅外部状态源 | [`usesyncexternalstore-subscribes-external-state.md`](usesyncexternalstore-subscribes-external-state.md) |
| Strict Mode 双次调用暴露副作用 | [`strict-mode-double-invokes-effects.md`](strict-mode-double-invokes-effects.md) |
| `useReducer` 把复杂状态转移集中到可测试的纯函数 | [`usereducer-centralizes-complex-state-transitions.md`](usereducer-centralizes-complex-state-transitions.md) |
| 状态机消除步骤流里的不可能状态 | [`state-machine-eliminates-impossible-ui-states.md`](state-machine-eliminates-impossible-ui-states.md) |
