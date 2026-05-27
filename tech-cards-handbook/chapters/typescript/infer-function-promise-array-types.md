# `infer` 可以提取函数、Promise 和数组内部类型

**问题**：如何从已有类型中推导出局部类型，而不是手写重复类型？

**要点**：

- `infer` 只能在条件类型里使用。
- 它相当于在匹配成功时声明一个临时类型变量。
- 内置 `ReturnType`、`Parameters`、`Awaited` 都是类似思路。

**示例**：

```typescript
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type ArrayElement<T> = T extends readonly (infer U)[] ? U : never;

type Equal<A, B> =
  (<T>() => T extends A ? 1 : 2) extends
  (<T>() => T extends B ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

function greet(name: string): string {
  return `hello ${name}`;
}

type A = Expect<Equal<MyReturnType<typeof greet>, string>>;
type B = Expect<Equal<UnwrapPromise<Promise<number>>, number>>;
type C = Expect<Equal<ArrayElement<string[]>, string>>;
type D = Expect<Equal<ArrayElement<readonly ["draft", "done"]>, "draft" | "done">>;
```

把代码保存为 `infer-function-promise-array-types.ts`，执行：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict infer-function-promise-array-types.ts
```

如果把 `type B` 的预期改成 `string`，编译器会报 `Type 'false' does not satisfy the constraint 'true'`，说明提取出的类型确实是 `number`。

**坑**：不要为了“类型体操”重写内置工具类型。生产代码优先使用 TypeScript 已经提供的工具。数组示例用 `readonly (infer U)[]`，这样普通数组和 `as const` 元组都能提取元素类型。

**检查**：类型提取是否能减少重复声明？如果只是让类型更炫，别用；如果能用 `Expect<Equal<...>>` 写出明确断言，再考虑沉淀成工具类型。
