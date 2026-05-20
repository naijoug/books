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
type ArrayElement<T> = T extends (infer U)[] ? U : never;

function greet(): string {
  return "hello";
}

type A = MyReturnType<typeof greet>;       // string
type B = UnwrapPromise<Promise<number>>;   // number
type C = ArrayElement<string[]>;           // string
```

**坑**：不要为了“类型体操”重写内置工具类型。生产代码优先使用 TypeScript 已经提供的工具。

**检查**：类型提取是否能减少重复声明？如果只是让类型更炫，别用。
