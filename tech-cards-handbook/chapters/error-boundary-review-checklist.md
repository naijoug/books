# 跨栈错误边界审查清单

> 这份清单把 Go、Rust、Python 和 TypeScript 错误传播、重试、调用方降级和对外错误码卡片串成一次可执行的代码审查。适用于审查 service、repository、handler 和 CLI command 的错误返回。

## 使用方法

1. 打开要审查的模块。
2. 按下面六个检查点逐项过。
3. 每个检查点附带对应的深度阅读卡片。
4. 记录不符合项，按优先级修复。

如果这次审查交给 agent 执行，可以直接调用 reviewer skill：`skills/skills/manual/review/error-boundary/`。建议把本清单作为背景材料，把待审模块、语言栈和对外接口路径作为输入，要求输出“错误决策表 + P0–P3 findings + 建议测试”。当输出过于笼统时，对照 `skills/skills/manual/review/error-boundary/references/sample-review-output.md` 校准；当语言栈差异导致漏检时，对照 `skills/skills/manual/review/error-boundary/references/language-probes.md` 补充 probe。

## Agent 审查输入模板

把下面模板贴给 agent，可以把一次错误边界审查限制在可复核、可接力的范围内；没有的信息用“未知”标出，不要让 agent 自行假设。

```text
请使用 skills/skills/manual/review/error-boundary/ 审查以下模块的错误边界。

语言栈：<Go / Python / Rust / TypeScript / mixed>
待审范围：<相对路径列表，精确到 module / handler / repository / service>
对外接口：<HTTP endpoint / CLI command / SDK method / background job output>
关键调用链：<入口 -> service -> adapter/repository -> external dependency>
已知错误类型：<领域错误、底层错误、第三方 SDK 错误；未知则写“未知”>
允许的恢复动作：<retry / degrade / return public error / escalate / unknown>
公开响应约束：<允许暴露的 code/message 字段；禁止暴露 SQL、host、path、token 等>
需要重点检查：<分类、cause/context 保留、重试耗尽、调用方降级、对外错误码翻译>

输出要求：
1. 先给出“底层错误 / 领域错误 / 调用方动作 / 重试或降级策略 / 对外 code-message / 证据路径”的决策表。
2. 再按 P0–P3 列出 findings，每条包含证据、风险、修复建议和建议测试。
3. 如果信息不足，列出需要补读的相对路径或需要开发者确认的问题，不要编造实现细节。
```

建议把 `待审范围` 控制在 3–8 个文件内；如果模块更大，先只审一条关键调用链。审查完成后，把决策表中缺失或冲突的项同步回“复审输出模板”。

## 决策表最小字段模板

如果团队还没有错误恢复决策表，不要一开始就追求完整矩阵；先用下面 7 个字段把一条关键调用链跑通。每一行只描述一种“底层失败如何变成调用方动作”。

| 底层错误/信号 | 领域错误 | 谁负责分类 | 调用方动作 | 重试/降级策略 | 对外 code/message | 诊断保留位置 |
|---|---|---|---|---|---|---|
| `SQL timeout` | `ProfileUnavailable` | `profiles/repository` | `return public error` | `retry 2 次后停止` | `PROFILE_UNAVAILABLE` / `profile temporarily unavailable` | `cause`、日志、trace |
| `404 from profile service` | `ProfileMissing` | `profile client adapter` | `degrade` | `不重试；由 recommendation service 返回默认头像并标记 degraded` | 无公开错误；响应带 `degraded=true` | metric、日志、trace |

最小填写规则：

1. **底层错误/信号** 写依赖层能观察到的事实，例如 SQL state、HTTP status、SDK exception、filesystem errno；这一列可以包含内部细节，但不能直接进入公开响应。
2. **领域错误** 写调用方稳定依赖的名字，例如 `ProfileMissing`、`OrderAlreadyExists`、`TemporaryStorageFailure`；如果写不出来，说明 adapter 还没有完成翻译。
3. **谁负责分类** 必须是一个相对路径或模块名，用来避免“每个调用方都重新猜一次错误字符串”。
4. **调用方动作** 只能从 `retry`、`degrade`、`return public error`、`escalate`、`ignore/observe` 中选；需要新动作时先补定义。
5. **重试/降级策略** 写可测试规则：次数、退避、哪些错误可降级、降级标记在哪里；不要只写“稍后重试”或“返回默认值”。
6. **对外 code/message** 只写用户或 API caller 可见的稳定字段；禁止把 SQL、host、path、token、SDK 原始 message 放进这一列。
7. **诊断保留位置** 写 `cause` / `__cause__` / `%w` / `inner` / log / trace / metric，确保安全响应和排障信息不会互相替代。

复审时优先找三类空洞：`领域错误` 为空（调用方无法分类）、`调用方动作` 为空（恢复策略被隐藏）、`诊断保留位置` 为空（修复公开泄漏时把根因也丢了）。

## 跨语言空表模板

把下面空表复制到具体项目的设计文档、PR 描述或 review comment 中，再按语言栈替换 `分类方式` 和 `诊断保留位置`。空表的价值是迫使团队先承认“这一列还不知道”，而不是让不同调用方各自猜错误字符串。

| 语言栈 | 底层错误/信号 | 分类方式 | 领域错误 | 调用方动作 | 重试/降级策略 | 对外 code/message | 诊断保留位置 | 建议测试 |
|---|---|---|---|---|---|---|---|---|
| Go |  | `errors.Is` / `errors.As` / sentinel error |  |  |  |  | `%w`、log、trace、metric |  |
| Python |  | custom exception hierarchy / `except SpecificError` |  |  |  |  | `__cause__`、log、trace、metric |  |
| Rust |  | `match` error enum / `thiserror` variant |  |  |  |  | `source()`、span、log、metric |  |
| TypeScript |  | `instanceof` / discriminated union / `AppError.code` |  |  |  |  | `cause` / `inner`、log、trace、metric |  |

填写时按这 4 步走：

1. 先选一条关键调用链，不要把全系统错误一次性塞进表里。
2. 每一行只允许一个底层错误信号；如果一行同时写 timeout、404、decode error，调用方动作通常会被写糊。
3. `分类方式` 必须写语言内可执行的机制，不写“看 message”或“根据日志判断”。
4. `建议测试` 至少覆盖一个公开响应脱敏断言和一个诊断保留断言，例如“不含 SQLSTATE / host / path，但 `cause` 保留原始错误”。

## 完整填写样例：Profile 查询调用链

下面是一条跨语言都能套用的填写样例。真实项目里不必一次写满所有语言；如果本次只审 TypeScript handler，就保留 TypeScript 那一行，把其他行删掉即可。

| 语言栈 | 底层错误/信号 | 分类方式 | 领域错误 | 调用方动作 | 重试/降级策略 | 对外 code/message | 诊断保留位置 | 建议测试 |
|---|---|---|---|---|---|---|---|---|
| Go | `context deadline exceeded` from `profiles.Repository.Get` | `errors.Is(err, context.DeadlineExceeded)` 后包装为领域错误 | `ProfileUnavailable` | `return public error` | `retry 2 次，指数退避；耗尽后停止，不降级付费资料页` | `PROFILE_UNAVAILABLE` / `profile temporarily unavailable` | `%w` cause、structured log、trace span | HTTP 响应不含 DSN/host/SQL；`errors.Is` 仍能命中 deadline；重试次数为 2 |
| Python | `psycopg.errors.UniqueViolation` 或 `OperationalError` | adapter 捕获具体异常并 `raise ProfileStoreError(...) from exc` | `ProfileStoreConflict` / `ProfileUnavailable` | `return public error` 或 `retry` | conflict 不重试；operational error 重试 2 次后转 `ProfileUnavailable` | `PROFILE_CONFLICT` 或 `PROFILE_UNAVAILABLE`，message 不含 SQLSTATE | `__cause__`、logger extra、metric label | 公开响应不含 SQLSTATE/table/index；`__cause__` 保留原始异常；conflict 不触发重试 |
| Rust | `sqlx::Error::RowNotFound` | `match` repository error enum variant | `ProfileMissing` | `degrade` | 不重试；recommendation 调用方返回默认头像并标记 `degraded=true` | 无公开错误；响应体包含 `degraded=true` | `source()`、`tracing` span、metric | 找不到 profile 时返回默认头像；trace 保留 query span；未知 DB error 不走降级 |
| TypeScript | `{ kind: "pool-exhausted", host: "10.0.0.8" }` from profile client | discriminated union + `translateStorageError()` | `ProfileUnavailable` | `return public error` | `isRetryable()` 允许 2 次；耗尽后转公开错误，不暴露 host | `PROFILE_UNAVAILABLE` / `profile temporarily unavailable` | `inner`、log context、trace id | 响应不含 `10.0.0.8` / path / SDK message；`inner` 保留原始对象；retry exhausted 可断言 |

这张表的关键不是“这些名字必须照抄”，而是每一行都能回答同一组问题：底层失败在哪里被分类，调用方能做什么，公开响应允许说什么，排障信息保留在哪里。若某一列只能写“看日志”或“由上层处理”，优先把它提升为 P1 finding。

## PR review comment 模板

当发现错误边界问题时，不要只留一句“这里要处理异常”。用下面的短评模板把证据、风险、期望决策表和建议测试一次写清，方便作者直接改，也方便后续 agent 复查。

如果用户只需要可粘贴 PR comments，而不是完整错误边界审查报告，让 agent 使用 `skills/skills/manual/review/error-boundary/references/sample-review-output.md` 里的 `PR-comments-only mode` 和 `PR-comments-only mini fixture` 校准输出：以 `## Error Boundary PR Comments` 开头，保留 1–3 条 `[error-boundary][P0/P1/P2]` 评论；每条必须包含具体相对路径证据、风险、期望决策表行和建议测试。

短评模式最容易出错的地方是“证据不足但硬写评论”。如果用户只说“给我 PR comments”，却没有提供 diff hunk、相对路径、函数名、public response contract 或错误流证据，先对照 `PR-comments-only insufficient-evidence fixture`：不要输出假的 P0/P1/P2 评论，不要编造行号、日志、trace、handler 名或隐藏实现细节；改为列出需要补充的审查目标，例如 `services/profile/http.ts` 的 catch/return 片段、adapter/service 错误映射、公开响应契约、失败测试或 trace。只有证据足以指向具体边界时，才进入短评模板。

```text
[error-boundary][P0/P1/P2] <一句话描述问题>

证据：<相对路径:行号 或 函数名> 现在把 <底层错误/信号> 直接变成 <公开响应 / 默认值 / 隐式重试 / 裸异常>。
风险：调用方无法稳定区分 <可重试 / 可降级 / 用户可见 / 内部故障>；公开响应可能泄漏 <SQLSTATE / host / path / SDK message>，或修复泄漏时丢失 cause。
期望决策表行：
- 底层错误/信号：<例如 SQL timeout / 404 / RowNotFound / pool-exhausted>
- 分类方式：<errors.Is / custom exception / match enum / discriminated union>
- 领域错误：<ProfileUnavailable / ProfileMissing / ...>
- 调用方动作：<retry / degrade / return public error / escalate>
- 对外 code/message：<PROFILE_UNAVAILABLE / 安全 message / 无公开错误>
- 诊断保留位置：<%w / __cause__ / source() / inner / log / trace>
建议测试：断言公开响应不含 <SQLSTATE / host / path / SDK message>，并断言 <cause / __cause__ / source() / inner> 保留根因；如果有 retry/degrade，再断言次数、标记和不可降级分支。
```

示例短评：

```text
[error-boundary][P1] profile client 把 404 和 timeout 都降级成空 Profile

证据：internal/profile/client.go GetProfile 直接 return Profile{}；service 无法知道是 ProfileMissing 还是 ProfileUnavailable。
风险：推荐页会把依赖故障误当成用户无资料，既不会重试，也不会打 degraded=true，排障时也没有 timeout cause。
期望决策表行：
- 底层错误/信号：HTTP 404；request timeout
- 分类方式：404 -> ErrProfileMissing；timeout -> ErrProfileUnavailable with %w
- 领域错误：ErrProfileMissing / ErrProfileUnavailable
- 调用方动作：404 degrade；timeout retry 后 return public error
- 对外 code/message：PROFILE_UNAVAILABLE / profile temporarily unavailable；404 降级路径无公开错误
- 诊断保留位置：%w、structured log、trace span
建议测试：404 返回默认头像且 degraded=true；timeout 重试 2 次后响应不含 host/path，errors.Is 仍能命中 deadline。
```

---

## 检查 1：失败是否进入类型系统？

| 问题 | 是 | 否 |
|---|---|---|
| 函数签名是否用 `Result<T, E>`（Rust）或 `error` 返回值（Go）表达"可能失败"？ | | |
| Python: 可能失败的路径是否抛出可分类异常，而不是返回 `None` / `{}` / `False` 让调用方猜？ | | |
| TypeScript: `catch (e: unknown)` 后是否先缩窄到自定义错误类型或 `Result` 分支，而不是直接读取 `message`？ | | |
| 调用方是否被迫处理失败，而不是靠空值、布尔标志或日志猜测？ | | |
| 失败原因是否写在错误类型里，而不是靠注释、日志或 panic？ | | |

**深度阅读：**
- Rust: [`rust/result-means-failable-with-reason.md`](rust/result-means-failable-with-reason.md)
- Python: [`python/custom-exception-hierarchy-makes-errors-classifiable.md`](python/custom-exception-hierarchy-makes-errors-classifiable.md)
- TypeScript: [`typescript/result-type-makes-errors-explicit.md`](typescript/result-type-makes-errors-explicit.md)

---

## 检查 2：错误上下文是否保留？

| 问题 | 是 | 否 |
|---|---|---|
| 每一层错误包装是否保留了"做什么、对谁做、为什么失败"？ | | |
| Go: 是否用 `fmt.Errorf("%w", err)` 保留根因链？ | | |
| Rust: 错误枚举是否包含足够的领域语义（而不仅是 `String`）？ | | |
| 是否能用 `errors.Is`/`errors.As`（Go）或 `match`（Rust）稳定地定位根因？ | | |
| Python: 是否用 `raise DomainError(...) from error` 保留 `__cause__` 链？ | | |

**深度阅读：**
- Go: [`go/errors-keep-context.md`](go/errors-keep-context.md)
- Python: [`python/external-error-codes-domain-defined-not-leaked.md`](python/external-error-codes-domain-defined-not-leaked.md)

---

## 检查 3：错误是否能被调用方稳定分类？

| 问题 | 是 | 否 |
|---|---|---|
| 调用方是否能区分"可重试"、"用户可见"、"内部故障"和"降级"？ | | |
| Go: 是否用 `errors.Is`/`errors.As` 而不是字符串匹配？ | | |
| Rust: 错误枚举变体是否覆盖所有领域失败场景？ | | |
| Python: 是否用自定义异常层级（`except NotFoundError`）而不是 `except ValueError` 加字符串判断？ | | |
| TypeScript: 是否用 `instanceof NotFoundError` / `instanceof RateLimitError` 等稳定类型缩窄，而不是字符串匹配？ | | |
| 是否存在 `_ =>`（Rust）或 `default:` （Go switch）或裸 `except Exception` 吞掉未知错误？ | | |

**深度阅读：**
- Go + Rust 对照: [`go/error-wrapping-vs-result-propagation.md`](go/error-wrapping-vs-result-propagation.md)
- Python: [`python/custom-exception-hierarchy-makes-errors-classifiable.md`](python/custom-exception-hierarchy-makes-errors-classifiable.md)
- TypeScript: [`typescript/custom-error-types-make-failures-classifiable.md`](typescript/custom-error-types-make-failures-classifiable.md)

---

## 检查 4：恢复动作是否显式化？

| 问题 | 是 | 否 |
|---|---|---|
| 可重试错误集合是否由领域定义（而不是靠 `strings.Contains`）？ | | |
| 最大重试次数、退避间隔是否可配置/可测试？ | | |
| Python: 重试耗尽是否抛出领域异常，并用 `raise ... from error` 保留最后一次根因？ | | |
| TypeScript: 是否把 `RetryPolicy` / `isRetryable()` 从 `catch` 分支里拆出来，并在耗尽后保留 `cause`？ | | |
| 重试耗尽后是否返回领域错误（保留上下文但不泄漏内部细节）？ | | |
| 是否存在嵌套 `match`/`if err != nil` 里的隐式重试？ | | |

**深度阅读：**
- Python: [`python/retry-policy-explicit-not-hidden-loop.md`](python/retry-policy-explicit-not-hidden-loop.md)
- TypeScript: [`typescript/retry-policy-explicit-not-hidden-catch.md`](typescript/retry-policy-explicit-not-hidden-catch.md)
- Rust: [`rust/retry-strategy-explicit-not-implicit-loop.md`](rust/retry-strategy-explicit-not-implicit-loop.md)
- Go: [`go/retry-policy-explicit-not-hidden-loop.md`](go/retry-policy-explicit-not-hidden-loop.md)

---

## 检查 5：降级决策是否留在调用方？

| 问题 | 是 | 否 |
|---|---|---|
| client / repository / SDK adapter 是否只返回真实结果和错误，而不是静默返回默认值？ | | |
| 调用方是否明确写出哪些错误可以降级，哪些错误必须继续传播？ | | |
| Python: 降级路径是否只捕获可降级异常，并用 `raise ... from error` 传播不可降级异常？ | | |
| TypeScript: 降级路径是否只捕获可降级错误（`instanceof ProfileNotFoundError`），并用 `new ProfileError(msg, inner)` 传播不可降级错误？ | | |
| 降级结果是否可观测，例如 `degraded=true`、metric、日志或 trace 标记？ | | |
| 不可降级路径是否仍保留错误链，让上层 handler / CLI 能继续分类？ | | |

**深度阅读：**
- Python: [`python/degradation-strategy-at-caller-not-callee.md`](python/degradation-strategy-at-caller-not-callee.md)
- Rust: [`rust/degradation-strategy-at-caller-not-callee.md`](rust/degradation-strategy-at-caller-not-callee.md)
- Go: [`go/degradation-strategy-at-caller-not-callee.md`](go/degradation-strategy-at-caller-not-callee.md)
- TypeScript: [`typescript/degradation-strategy-at-caller-not-callee.md`](typescript/degradation-strategy-at-caller-not-callee.md)

---

## 检查 6：对外错误码是否来自领域？

| 问题 | 是 | 否 |
|---|---|---|
| 对外响应的错误码是否由领域枚举或领域异常定义？ | | |
| SQL state、驱动类型名、第三方 SDK 错误是否在 adapter 层翻译成领域错误码？ | | |
| Python 是否用 `raise DomainError(...) from error` 保留异常链，但只输出安全 `code` / `message`？ | | |
| TypeScript 是否把底层 `StorageError` / SDK error 翻译成 `AppError.code`，并用 `inner` / `cause` 保留根因？ | | |
| 内部错误细节是否只进日志，不进对外响应？ | | |
| 对外消息是否直接拼接了底层错误字符串？ | | |

**深度阅读：**
- Python: [`python/external-error-codes-domain-defined-not-leaked.md`](python/external-error-codes-domain-defined-not-leaked.md)
- Rust: [`rust/external-error-codes-domain-defined-not-leaked.md`](rust/external-error-codes-domain-defined-not-leaked.md)
- Go: [`go/external-error-codes-domain-defined-not-leaked.md`](go/external-error-codes-domain-defined-not-leaked.md)
- TypeScript: [`typescript/external-error-codes-domain-defined-not-leaked.md`](typescript/external-error-codes-domain-defined-not-leaked.md)

---

## 复审输出模板

完成检查后，把不符合项填入下表，按优先级排序；如果恢复路径已经被统一到决策表，也把对应证据写进去，方便下一次 review 直接复查。

| 检查点 | 不符合描述 | 涉及文件 | 修复方案 | 决策表/证据 | 优先级 |
|---|---|---|---|---|---|
| | | | | | |

如果团队还没有决策表，可以先参考 Python 卡片 [`python/error-recovery-path-needs-one-decision-table.md`](python/error-recovery-path-needs-one-decision-table.md)、Go 卡片 [`go/error-recovery-path-needs-one-decision-table.md`](go/error-recovery-path-needs-one-decision-table.md)、Rust 卡片 [`rust/error-recovery-path-needs-one-decision-table.md`](rust/error-recovery-path-needs-one-decision-table.md) 或 TypeScript 卡片 [`typescript/error-recovery-path-needs-one-decision-table.md`](typescript/error-recovery-path-needs-one-decision-table.md)，把错误类型、恢复动作、对外错误码和是否降级/重试整理到一张表里。

## 复审输出示例

下面是一次 10 分钟错误边界走查可以留下的最小记录。重点不是写长报告，而是把“哪里会让调用方失去决策能力”记录成可执行修复项，并指出后续应该补到哪张决策表。

| 检查点 | 不符合描述 | 涉及文件 | 修复方案 | 决策表/证据 | 优先级 |
|---|---|---|---|---|---|
| 检查 5：降级决策是否留在调用方？ | `ProfileClient.Get` 在 404、timeout 和 JSON decode 失败时都返回空 `Profile{}`，service 无法区分“用户不存在”和“依赖故障”，也无法打 `degraded=true`。 | `internal/profile/client.go`、`internal/recommend/service.go` | client 只返回真实错误：404 映射为 `ErrProfileMissing`，timeout 保留 `%w` 根因；`RecommendationService` 只对 `ErrProfileMissing` 降级，并在响应里标记 `Degraded: true`。 | 在 profile 错误决策表中新增 `ErrProfileMissing -> DEGRADE`，timeout / decode 失败保持 `ESCALATE`。 | P1 |
| 检查 4：恢复动作是否显式化？ | `OrderRepository.Save` 内部固定重试 5 次，没有退避参数，也没有把重试耗尽映射成领域错误。 | `internal/order/repository.go` | 抽出 `RetryPolicy`，只对 `ErrTransientStorage` 重试；耗尽后返回 `OrderSaveUnavailable` 并保留错误链。 | `ErrTransientStorage -> RETRY`，耗尽后 `OrderSaveUnavailable -> RETURN_PUBLIC_ERROR`。 | P1 |
| 检查 6：对外错误码是否来自领域？ | handler 直接把 `pq: duplicate key value violates unique constraint` 拼进 HTTP response。 | `internal/http/order_handler.go` | repository 映射为 `ErrOrderAlreadyExists`，handler 统一输出 `ORDER_ALREADY_EXISTS`；底层错误只进日志。 | `ErrOrderAlreadyExists -> RETURN_PUBLIC_ERROR / ORDER_ALREADY_EXISTS`，底层 `pq` 错误只作为 cause。 | P0 |
| 检查 2 + 检查 4：错误上下文和恢复动作是否保留？ | Python `load_profile()` 在 `except Exception` 中直接 `return {}`，既丢失 `__cause__`，又让调用方不知道该重试、降级还是返回公开错误。 | `profiles/repository.py`、`profiles/service.py` | repository 把底层异常翻译成 `ProfileNotFoundError` / `TemporaryProfileError` 并使用 `raise ... from error`；service 通过 `RetryPolicy` 只重试临时错误，耗尽后抛出 `ProfileUnavailableError`。 | `ProfileNotFoundError -> DEGRADE`，`TemporaryProfileError -> RETRY`，耗尽后 `ProfileUnavailableError -> RETURN_PUBLIC_ERROR / PROFILE_UNAVAILABLE`。 | P1 |

优先级参考：
- **P0**: 错误码泄漏内部细节（SQL state、连接字符串、文件路径）→ 立即修复。
- **P1**: 隐式重试、`strings.Contains` 匹配或静默默认值导致调用方无法分类 → 本迭代修复。
- **P2**: 缺少 `Result` / `%w` 包装 → 重构时补齐。
- **P3**: 退避间隔不可配置 → 后续迭代优化。
