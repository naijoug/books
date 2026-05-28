# TypeScript 技术卡片

本目录按“一张卡片一个 Markdown 文件”维护，共 10 张。文件名使用英文 `kebab-case`。

| 卡片 | 文件 |
|---|---|
| 用联合类型表达状态机 | [`union-types-state-machine.md`](union-types-state-machine.md) |
| `infer` 用于从类型里提取信息 | [`typescript-infer-extracts-types.md`](typescript-infer-extracts-types.md) |
| 条件类型让类型根据输入变化 | [`conditional-types-input-dependent.md`](conditional-types-input-dependent.md) |
| `infer` 可以提取函数、Promise 和数组内部类型 | [`infer-function-promise-array-types.md`](infer-function-promise-array-types.md) |
| Mapped Type + 条件类型可以按值类型筛选字段 | [`mapped-type-filter-fields-by-value.md`](mapped-type-filter-fields-by-value.md) |
| 深度只读类型要谨慎处理对象边界 | [`deep-readonly-object-boundaries.md`](deep-readonly-object-boundaries.md) |
| `satisfies` 检查形状但保留推断 | [`satisfies-checks-shape-keeps-inference.md`](satisfies-checks-shape-keeps-inference.md) |
| `unknown` 要先缩窄再使用 | [`unknown-requires-narrowing.md`](unknown-requires-narrowing.md) |
| 模板字面量类型约束字符串格式 | [`template-literal-types-constrain-strings.md`](template-literal-types-constrain-strings.md) |
| 工具类型从领域模型派生 DTO | [`utility-types-derive-dtos.md`](utility-types-derive-dtos.md) |

## 可运行验证索引

当前 10 张 TypeScript 卡片都应能通过 `tsc --noEmit --strict` 做最小类型检查。维护原则：示例优先写成可复制的 `.ts` 片段；类型体操类卡片至少保留 `Expect<Equal<...>>` 断言；涉及浏览器 API、`console` 或现代内建对象时显式写出 `--lib`，避免读者在默认环境下遇到无关报错。

| 类型 | 卡片 | 验证方式 |
|---|---|---|
| 状态建模 | [`union-types-state-machine.md`](union-types-state-machine.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom union-types-state-machine.ts` |
| 类型提取 | [`typescript-infer-extracts-types.md`](typescript-infer-extracts-types.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict typescript-infer-extracts-types.ts` |
| 类型提取 | [`infer-function-promise-array-types.md`](infer-function-promise-array-types.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict infer-function-promise-array-types.ts` |
| 条件类型 | [`conditional-types-input-dependent.md`](conditional-types-input-dependent.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict conditional-types-input-dependent.ts` |
| 映射类型 | [`mapped-type-filter-fields-by-value.md`](mapped-type-filter-fields-by-value.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict mapped-type-filter-fields-by-value.ts` |
| 只读边界 | [`deep-readonly-object-boundaries.md`](deep-readonly-object-boundaries.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom deep-readonly-object-boundaries.ts` |
| 形状检查 | [`satisfies-checks-shape-keeps-inference.md`](satisfies-checks-shape-keeps-inference.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom satisfies-checks-shape-keeps-inference.ts` |
| 输入缩窄 | [`unknown-requires-narrowing.md`](unknown-requires-narrowing.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom unknown-requires-narrowing.ts` |
| 字符串约束 | [`template-literal-types-constrain-strings.md`](template-literal-types-constrain-strings.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom template-literal-types-constrain-strings.ts` |
| DTO 派生 | [`utility-types-derive-dtos.md`](utility-types-derive-dtos.md) | `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom utility-types-derive-dtos.ts` |
