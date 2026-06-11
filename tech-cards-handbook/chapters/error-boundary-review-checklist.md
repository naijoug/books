# 跨栈错误边界审查清单

> 这份清单把 Go、Rust 和 Python 错误传播、重试、调用方降级和对外错误码卡片串成一次可执行的代码审查。适用于审查 service、repository、handler 和 CLI command 的错误返回。

## 使用方法

1. 打开要审查的模块。
2. 按下面六个检查点逐项过。
3. 每个检查点附带对应的深度阅读卡片。
4. 记录不符合项，按优先级修复。

---

## 检查 1：失败是否进入类型系统？

| 问题 | 是 | 否 |
|---|---|---|
| 函数签名是否用 `Result<T, E>`（Rust）或 `error` 返回值（Go）表达"可能失败"？ | | |
| Python: 可能失败的路径是否抛出可分类异常，而不是返回 `None` / `{}` / `False` 让调用方猜？ | | |
| 调用方是否被迫处理失败，而不是靠空值、布尔标志或日志猜测？ | | |
| 失败原因是否写在错误类型里，而不是靠注释、日志或 panic？ | | |

**深度阅读：**
- Rust: [`rust/result-means-failable-with-reason.md`](rust/result-means-failable-with-reason.md)
- Python: [`python/custom-exception-hierarchy-makes-errors-classifiable.md`](python/custom-exception-hierarchy-makes-errors-classifiable.md)

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
| 是否存在 `_ =>`（Rust）或 `default:` （Go switch）或裸 `except Exception` 吞掉未知错误？ | | |

**深度阅读：**
- Go + Rust 对照: [`go/error-wrapping-vs-result-propagation.md`](go/error-wrapping-vs-result-propagation.md)
- Python: [`python/custom-exception-hierarchy-makes-errors-classifiable.md`](python/custom-exception-hierarchy-makes-errors-classifiable.md)

---

## 检查 4：恢复动作是否显式化？

| 问题 | 是 | 否 |
|---|---|---|
| 可重试错误集合是否由领域定义（而不是靠 `strings.Contains`）？ | | |
| 最大重试次数、退避间隔是否可配置/可测试？ | | |
| Python: 重试耗尽是否抛出领域异常，并用 `raise ... from error` 保留最后一次根因？ | | |
| 重试耗尽后是否返回领域错误（保留上下文但不泄漏内部细节）？ | | |
| 是否存在嵌套 `match`/`if err != nil` 里的隐式重试？ | | |

**深度阅读：**
- Python: [`python/retry-policy-explicit-not-hidden-loop.md`](python/retry-policy-explicit-not-hidden-loop.md)
- Rust: [`rust/retry-strategy-explicit-not-implicit-loop.md`](rust/retry-strategy-explicit-not-implicit-loop.md)
- Go: [`go/retry-policy-explicit-not-hidden-loop.md`](go/retry-policy-explicit-not-hidden-loop.md)

---

## 检查 5：降级决策是否留在调用方？

| 问题 | 是 | 否 |
|---|---|---|
| client / repository / SDK adapter 是否只返回真实结果和错误，而不是静默返回默认值？ | | |
| 调用方是否明确写出哪些错误可以降级，哪些错误必须继续传播？ | | |
| Python: 降级路径是否只捕获可降级异常，并用 `raise ... from error` 传播不可降级异常？ | | |
| 降级结果是否可观测，例如 `degraded=true`、metric、日志或 trace 标记？ | | |
| 不可降级路径是否仍保留错误链，让上层 handler / CLI 能继续分类？ | | |

**深度阅读：**
- Python: [`python/degradation-strategy-at-caller-not-callee.md`](python/degradation-strategy-at-caller-not-callee.md)
- Rust: [`rust/degradation-strategy-at-caller-not-callee.md`](rust/degradation-strategy-at-caller-not-callee.md)
- Go: [`go/degradation-strategy-at-caller-not-callee.md`](go/degradation-strategy-at-caller-not-callee.md)

---

## 检查 6：对外错误码是否来自领域？

| 问题 | 是 | 否 |
|---|---|---|
| 对外响应的错误码是否由领域枚举或领域异常定义？ | | |
| SQL state、驱动类型名、第三方 SDK 错误是否在 adapter 层翻译成领域错误码？ | | |
| Python 是否用 `raise DomainError(...) from error` 保留异常链，但只输出安全 `code` / `message`？ | | |
| 内部错误细节是否只进日志，不进对外响应？ | | |
| 对外消息是否直接拼接了底层错误字符串？ | | |

**深度阅读：**
- Python: [`python/external-error-codes-domain-defined-not-leaked.md`](python/external-error-codes-domain-defined-not-leaked.md)
- Rust: [`rust/external-error-codes-domain-defined-not-leaked.md`](rust/external-error-codes-domain-defined-not-leaked.md)
- Go: [`go/external-error-codes-domain-defined-not-leaked.md`](go/external-error-codes-domain-defined-not-leaked.md)

---

## 复审输出模板

完成检查后，把不符合项填入下表，按优先级排序；如果恢复路径已经被统一到决策表，也把对应证据写进去，方便下一次 review 直接复查。

| 检查点 | 不符合描述 | 涉及文件 | 修复方案 | 决策表/证据 | 优先级 |
|---|---|---|---|---|---|
| | | | | | |

如果团队还没有决策表，可以先参考 Python 卡片 [`python/error-recovery-path-needs-one-decision-table.md`](python/error-recovery-path-needs-one-decision-table.md)、Go 卡片 [`go/error-recovery-path-needs-one-decision-table.md`](go/error-recovery-path-needs-one-decision-table.md) 或 Rust 卡片 [`rust/error-recovery-path-needs-one-decision-table.md`](rust/error-recovery-path-needs-one-decision-table.md)，把错误类型、恢复动作、对外错误码和是否降级/重试整理到一张表里。

## 复审输出示例

下面是一次 10 分钟错误边界走查可以留下的最小记录。重点不是写长报告，而是把“哪里会让调用方失去决策能力”记录成可执行修复项，并指出后续应该补到哪张决策表。

| 检查点 | 不符合描述 | 涉及文件 | 修复方案 | 决策表/证据 | 优先级 |
|---|---|---|---|---|---|
| 检查 5：降级决策是否留在调用方？ | `ProfileClient.Get` 在 404、timeout 和 JSON decode 失败时都返回空 `Profile{}`，service 无法区分“用户不存在”和“依赖故障”，也无法打 `degraded=true`。 | `internal/profile/client.go`、`internal/recommend/service.go` | client 只返回真实错误：404 映射为 `ErrProfileMissing`，timeout 保留 `%w` 根因；`RecommendationService` 只对 `ErrProfileMissing` 降级，并在响应里标记 `Degraded: true`。 | 在 profile 错误决策表中新增 `ErrProfileMissing -> DEGRADE`，timeout / decode 失败保持 `ESCALATE`。 | P1 |
| 检查 4：恢复动作是否显式化？ | `OrderRepository.Save` 内部固定重试 5 次，没有退避参数，也没有把重试耗尽映射成领域错误。 | `internal/order/repository.go` | 抽出 `RetryPolicy`，只对 `ErrTransientStorage` 重试；耗尽后返回 `OrderSaveUnavailable` 并保留错误链。 | `ErrTransientStorage -> RETRY`，耗尽后 `OrderSaveUnavailable -> RETURN_PUBLIC_ERROR`。 | P1 |
| 检查 6：对外错误码是否来自领域？ | handler 直接把 `pq: duplicate key value violates unique constraint` 拼进 HTTP response。 | `internal/http/order_handler.go` | repository 映射为 `ErrOrderAlreadyExists`，handler 统一输出 `ORDER_ALREADY_EXISTS`；底层错误只进日志。 | `ErrOrderAlreadyExists -> RETURN_PUBLIC_ERROR / ORDER_ALREADY_EXISTS`，底层 `pq` 错误只作为 cause。 | P0 |

优先级参考：
- **P0**: 错误码泄漏内部细节（SQL state、连接字符串、文件路径）→ 立即修复。
- **P1**: 隐式重试、`strings.Contains` 匹配或静默默认值导致调用方无法分类 → 本迭代修复。
- **P2**: 缺少 `Result` / `%w` 包装 → 重构时补齐。
- **P3**: 退避间隔不可配置 → 后续迭代优化。
