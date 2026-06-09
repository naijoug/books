# TypeScript 技术卡片

本目录按"一张卡片一个 Markdown 文件"维护，共 25 张。文件名使用英文 `kebab-case`。

| 卡片 | 文件 |
|---|---|
| 用联合类型表达状态机 | [`union-types-state-machine.md`](union-types-state-machine.md) |
| `never` 穷尽检查防止漏掉状态分支 | [`never-exhaustive-state-checks.md`](never-exhaustive-state-checks.md) |
| `infer` 用于从类型里提取信息 | [`typescript-infer-extracts-types.md`](typescript-infer-extracts-types.md) |
| 条件类型让类型根据输入变化 | [`conditional-types-input-dependent.md`](conditional-types-input-dependent.md) |
| `infer` 可以提取函数、Promise 和数组内部类型 | [`infer-function-promise-array-types.md`](infer-function-promise-array-types.md) |
| Mapped Type + 条件类型可以按值类型筛选字段 | [`mapped-type-filter-fields-by-value.md`](mapped-type-filter-fields-by-value.md) |
| 深度只读类型要谨慎处理对象边界 | [`deep-readonly-object-boundaries.md`](deep-readonly-object-boundaries.md) |
| `satisfies` 检查形状但保留推断 | [`satisfies-checks-shape-keeps-inference.md`](satisfies-checks-shape-keeps-inference.md) |
| `unknown` 要先缩窄再使用 | [`unknown-requires-narrowing.md`](unknown-requires-narrowing.md) |
| 类型守卫把外部输入缩窄成领域对象 | [`type-guards-narrow-domain-inputs.md`](type-guards-narrow-domain-inputs.md) |
| 断言函数让边界错误提前失败 | [`assertion-functions-fail-fast-boundaries.md`](assertion-functions-fail-fast-boundaries.md) |
| 外部 API 响应先过 schema 边界 | [`external-api-response-schema-boundary.md`](external-api-response-schema-boundary.md) |
| 请求状态和数据 schema 分层 | [`request-state-keeps-schema-data-separate.md`](request-state-keeps-schema-data-separate.md) |
| 模板字面量类型约束字符串格式 | [`template-literal-types-constrain-strings.md`](template-literal-types-constrain-strings.md) |
| 品牌类型防止不同 ID 互相混用 | [`branded-types-prevent-id-mixing.md`](branded-types-prevent-id-mixing.md) |
| Result 类型让错误处理显式 | [`result-type-makes-errors-explicit.md`](result-type-makes-errors-explicit.md) |
| 工具类型从领域模型派生 DTO | [`utility-types-derive-dtos.md`](utility-types-derive-dtos.md) |
| DTO 边界不要泄漏领域模型 | [`dto-boundary-hides-domain-model.md`](dto-boundary-hides-domain-model.md) |
| API DTO 版本演进不要回灌领域模型 | [`api-dto-version-does-not-backflow-domain-model.md`](api-dto-version-does-not-backflow-domain-model.md) |
| 弃用 DTO 字段要有迁移窗口和测试 | [`deprecated-dto-fields-need-migration-window-tests.md`](deprecated-dto-fields-need-migration-window-tests.md) |
| 领域事件不要复用 API DTO | [`domain-events-do-not-reuse-api-dtos.md`](domain-events-do-not-reuse-api-dtos.md) |
| Domain Event 与 Integration Event 要分层 | [`domain-event-integration-event-layering.md`](domain-event-integration-event-layering.md) |
| 不要用万能 mapper 跨多条边界 | [`universal-mapper-crosses-too-many-boundaries.md`](universal-mapper-crosses-too-many-boundaries.md) |
| ViewModel 不要污染领域模型 | [`view-model-keeps-ui-state-out-of-domain.md`](view-model-keeps-ui-state-out-of-domain.md) |
| 表单命令对象不要复用 ViewModel | [`form-command-does-not-reuse-view-model.md`](form-command-does-not-reuse-view-model.md) |

## 边界建模阅读线

以下卡片按“输入 → 领域 → 输出 → 展示 → 提交”的顺序排列，覆盖一个 TypeScript 应用从外部数据进入、被业务层处理、再离开业务层的常见边界。每张卡片承接上一张的问题，建议按序阅读。

### 1. 输入边界：先承认外部数据不可信

1. **`unknown` 要先缩窄再使用** ([`unknown-requires-narrowing.md`](unknown-requires-narrowing.md)) — 建立前提：外部数据一律以 `unknown` 进入，不信任、不假设。
2. **类型守卫把外部输入缩窄成领域对象** ([`type-guards-narrow-domain-inputs.md`](type-guards-narrow-domain-inputs.md)) — 用 `is` / `in` / `typeof` 把 `unknown` 缩窄为可用的联合分支。
3. **断言函数让边界错误提前失败** ([`assertion-functions-fail-fast-boundaries.md`](assertion-functions-fail-fast-boundaries.md)) — 在入口处断言不变量，失败立刻抛出，避免错误向下传播。
4. **外部 API 响应先过 schema 边界** ([`external-api-response-schema-boundary.md`](external-api-response-schema-boundary.md)) — 把 decoder / schema 检查集中在网络边界，业务层只处理已验证的数据。

### 2. 领域边界：把状态、身份和错误建模清楚

5. **请求状态和数据 schema 分层** ([`request-state-keeps-schema-data-separate.md`](request-state-keeps-schema-data-separate.md)) — 把请求生命周期（idle/loading/success/failure）和已验证数据分开建模。
6. **品牌类型防止不同 ID 互相混用** ([`branded-types-prevent-id-mixing.md`](branded-types-prevent-id-mixing.md)) — 在领域边界给原始类型打标，防止用户 ID、订单 ID、商品 ID 等跨边界混用。
7. **Result 类型让错误处理显式** ([`result-type-makes-errors-explicit.md`](result-type-makes-errors-explicit.md)) — 用 `Result<T,E>` 表达可恢复业务错误，把 `throw` 留给不可恢复异常。
8. **`never` 穷尽检查防止漏掉状态分支** ([`never-exhaustive-state-checks.md`](never-exhaustive-state-checks.md)) — 在 switch / if-else 链末尾用 `assertNever` 保证所有分支都被处理。

### 3. 输出边界：不要让领域模型直接暴露出去

这一段可以分成三组读：先学会从领域模型导出可公开 DTO，再处理 API 版本演进，最后把事件发布边界拆成内部事实和外部契约。读完后应能回答：“这份数据是给 HTTP 客户端、消息消费者，还是 UI 组件用？”

**3.1 HTTP / RPC 输出契约**

9. **工具类型从领域模型派生 DTO** ([`utility-types-derive-dtos.md`](utility-types-derive-dtos.md)) — 用 `Pick` / `Omit` / `Partial` 等从领域类型派生 API 层 DTO，避免手工同步。
10. **DTO 边界不要泄漏领域模型** ([`dto-boundary-hides-domain-model.md`](dto-boundary-hides-domain-model.md)) — 用 mapper 固化公开 DTO、管理脱敏和字段格式转换，避免领域模型穿透外部边界。
11. **API DTO 版本演进不要回灌领域模型** ([`api-dto-version-does-not-backflow-domain-model.md`](api-dto-version-does-not-backflow-domain-model.md)) — 把 v1 / v2 兼容逻辑留在 adapter 和 mapper，避免旧字段名、别名和迁移窗口污染领域模型。
12. **弃用 DTO 字段要有迁移窗口和测试** ([`deprecated-dto-fields-need-migration-window-tests.md`](deprecated-dto-fields-need-migration-window-tests.md)) — 对字段重命名和替换保留迁移窗口、弃用标记和契约测试，避免“类型删了但消费者还在用”。

**3.2 事件发布契约**

13. **领域事件不要复用 API DTO** ([`domain-events-do-not-reuse-api-dtos.md`](domain-events-do-not-reuse-api-dtos.md)) — 把 HTTP 请求/响应契约和“业务事实已发生”的事件 payload 分开，避免 API 版本变化拖动消息消费者。
14. **Domain Event 与 Integration Event 要分层** ([`domain-event-integration-event-layering.md`](domain-event-integration-event-layering.md)) — 在发布边界把内部领域事件转换成外部集成事件，避免内部重构破坏跨服务契约。

**3.3 单边界 mapper 规则**

15. **不要用万能 mapper 跨多条边界** ([`universal-mapper-crosses-too-many-boundaries.md`](universal-mapper-crosses-too-many-boundaries.md)) — 把 DTO、ViewModel、Command、Event 的转换拆成单边界 mapper，避免一个函数同时承担多层职责。

### 4. 展示与提交边界：UI 状态只在 UI 层停留

16. **ViewModel 不要污染领域模型** ([`view-model-keeps-ui-state-out-of-domain.md`](view-model-keeps-ui-state-out-of-domain.md)) — 把页面展示字段、选中态、格式化文本和跳转链接留在 ViewModel，避免 UI 临时状态反向污染领域模型。
17. **表单命令对象不要复用 ViewModel** ([`form-command-does-not-reuse-view-model.md`](form-command-does-not-reuse-view-model.md)) — 提交前从表单 ViewModel 构造明确 command，丢弃错误提示、脏字段、按钮状态和展示文案。

如果只想快速复习，可以按四个自检问题回看：输入是否先验证，领域是否表达业务不变量，输出是否经过 DTO mapper，提交是否从 ViewModel 转换成 command。

## 边界 mapper 命名约定

边界越多，越需要让函数名直接暴露“从哪里来、到哪里去”。本章示例优先采用下面的命名，避免一个 `mapProduct` 同时承担输入校验、DTO 脱敏、页面格式化和提交转换等职责。

| 命名 | 方向 | 适用位置 | 不该做的事 |
|---|---|---|---|
| `parseXxx` / `decodeXxx` | `unknown` / raw → 已验证输入 | 网络、CLI、表单入口 | 不读取数据库，不调用业务服务 |
| `toXxxDto` | 领域模型 → API DTO | controller、route handler、RPC resolver | 不返回领域对象引用，不泄漏内部字段 |
| `fromXxxDto` | API DTO → 领域命令或领域输入 | client adapter、integration adapter | 不把 DTO 当成领域模型长期保存 |
| `toXxxViewModel` | 领域模型 / DTO → 页面展示模型 | page loader、component adapter | 不写回业务状态，不保存临时 UI 字段到领域层 |
| `toXxxCommand` | 表单 ViewModel → 业务命令 | submit handler、action、mutation | 不携带错误提示、按钮状态、格式化文案 |
| `toXxxEvent` | 领域结果 → domain / integration event | use case、transaction boundary | 不复用 HTTP response DTO，不塞入 UI 字段 |

维护规则：同一个 mapper 只跨越一条边界；如果函数名里说不清 `from` / `to`，通常说明它承担了两个以上职责，应该拆开。目录里新增卡片时，也优先按这个命名给示例函数命名。

## 可运行验证索引

当前 25 张 TypeScript 卡片都应能通过 `tsc --noEmit --strict` 做最小类型检查。维护原则:示例优先写成可复制的 `.ts` 片段;类型体操类卡片至少保留 `Expect<Equal<...>>` 断言;涉及浏览器 API、`console` 或现代内建对象时显式写出 `--lib`,避免读者在默认环境下遇到无关报错。

章节级批量复核可从 `books` 仓库根目录运行:

```bash
python3 scripts/verify_typescript_cards.py
```

脚本会从本章 Markdown 中抽取 `ts` / `typescript` 代码块,按卡片合并写入临时 `.ts` 文件,并用 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom` 逐张检查。当前预期输出为 `verified 25 TypeScript cards with 26 code blocks`。

| 类型 | 卡片 | 验证方式 |
|---|---|---|
| 状态建模 | [`union-types-state-machine.md`](union-types-state-machine.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom union-types-state-machine.ts` |
| 状态建模 | [`never-exhaustive-state-checks.md`](never-exhaustive-state-checks.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom never-exhaustive-state-checks.ts` |
| 类型提取 | [`typescript-infer-extracts-types.md`](typescript-infer-extracts-types.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict typescript-infer-extracts-types.ts` |
| 类型提取 | [`infer-function-promise-array-types.md`](infer-function-promise-array-types.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict infer-function-promise-array-types.ts` |
| 条件类型 | [`conditional-types-input-dependent.md`](conditional-types-input-dependent.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict conditional-types-input-dependent.ts` |
| 映射类型 | [`mapped-type-filter-fields-by-value.md`](mapped-type-filter-fields-by-value.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict mapped-type-filter-fields-by-value.ts` |
| 只读边界 | [`deep-readonly-object-boundaries.md`](deep-readonly-object-boundaries.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom deep-readonly-object-boundaries.ts` |
| 形状检查 | [`satisfies-checks-shape-keeps-inference.md`](satisfies-checks-shape-keeps-inference.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom satisfies-checks-shape-keeps-inference.ts` |
| 输入缩窄 | [`unknown-requires-narrowing.md`](unknown-requires-narrowing.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom unknown-requires-narrowing.ts` |
| 输入缩窄 | [`type-guards-narrow-domain-inputs.md`](type-guards-narrow-domain-inputs.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom type-guards-narrow-domain-inputs.ts` |
| 输入断言 | [`assertion-functions-fail-fast-boundaries.md`](assertion-functions-fail-fast-boundaries.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom assertion-functions-fail-fast-boundaries.ts` |
| Schema 边界 | [`external-api-response-schema-boundary.md`](external-api-response-schema-boundary.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom external-api-response-schema-boundary.ts` |
| 请求状态 | [`request-state-keeps-schema-data-separate.md`](request-state-keeps-schema-data-separate.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom request-state-keeps-schema-data-separate.ts` |
| 字符串约束 | [`template-literal-types-constrain-strings.md`](template-literal-types-constrain-strings.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom template-literal-types-constrain-strings.ts` |
| 领域隔离 | [`branded-types-prevent-id-mixing.md`](branded-types-prevent-id-mixing.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom branded-types-prevent-id-mixing.ts` |
| 错误建模 | [`result-type-makes-errors-explicit.md`](result-type-makes-errors-explicit.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom result-type-makes-errors-explicit.ts` |
| DTO 派生 | [`utility-types-derive-dtos.md`](utility-types-derive-dtos.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom utility-types-derive-dtos.ts` |
| DTO 边界 | [`dto-boundary-hides-domain-model.md`](dto-boundary-hides-domain-model.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom dto-boundary-hides-domain-model.ts` |
| DTO 版本 | [`api-dto-version-does-not-backflow-domain-model.md`](api-dto-version-does-not-backflow-domain-model.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom api-dto-version-does-not-backflow-domain-model.ts` |
| DTO 迁移 | [`deprecated-dto-fields-need-migration-window-tests.md`](deprecated-dto-fields-need-migration-window-tests.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom deprecated-dto-fields-need-migration-window-tests.ts` |
| 事件边界 | [`domain-events-do-not-reuse-api-dtos.md`](domain-events-do-not-reuse-api-dtos.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom domain-events-do-not-reuse-api-dtos.ts` |
| 事件边界 | [`domain-event-integration-event-layering.md`](domain-event-integration-event-layering.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom domain-event-integration-event-layering.ts` |
| 边界 mapper | [`universal-mapper-crosses-too-many-boundaries.md`](universal-mapper-crosses-too-many-boundaries.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom universal-mapper-crosses-too-many-boundaries.ts` |
| ViewModel 边界 | [`view-model-keeps-ui-state-out-of-domain.md`](view-model-keeps-ui-state-out-of-domain.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom view-model-keeps-ui-state-out-of-domain.ts` |
| Command 边界 | [`form-command-does-not-reuse-view-model.md`](form-command-does-not-reuse-view-model.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom form-command-does-not-reuse-view-model.ts` |
