# 深度只读类型要谨慎处理对象边界

**问题**：如何让嵌套配置对象在编译期不可修改？

**要点**：

- `readonly` 只作用于当前层。
- 递归 mapped type 可以实现深度只读。
- 函数、Date、Map 等特殊对象不适合简单递归。

**示例**：

```typescript
type Primitive = string | number | boolean | bigint | symbol | null | undefined;
type Builtin = Primitive | Date | RegExp | Error | Function;

type DeepReadonly<T> = T extends Builtin
  ? T
  : T extends Map<infer K, infer V>
    ? ReadonlyMap<DeepReadonly<K>, DeepReadonly<V>>
    : T extends Set<infer V>
      ? ReadonlySet<DeepReadonly<V>>
      : T extends readonly (infer U)[]
        ? readonly DeepReadonly<U>[]
        : { readonly [K in keyof T]: DeepReadonly<T[K]> };

interface Config {
  database: {
    host: string;
    port: number;
  };
  hooks: {
    onConnect: () => void;
  };
  releasedAt: Date;
  replicas: Array<{ host: string }>;
}

const config: DeepReadonly<Config> = {
  database: { host: "localhost", port: 5432 },
  hooks: { onConnect: () => undefined },
  releasedAt: new Date("2026-01-01"),
  replicas: [{ host: "replica-1" }],
};

config.hooks.onConnect();
config.releasedAt.getFullYear();

// config.database.host = "prod"; // 编译错误：嵌套字段只读
// config.replicas.push({ host: "replica-2" }); // 编译错误：数组变成只读数组
// config.replicas[0].host = "prod"; // 编译错误：数组元素也被递归只读
```

最小验证：把代码保存为 `deep-readonly-object-boundaries.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom deep-readonly-object-boundaries.ts` 应通过；取消任意一行赋值/`push` 注释后，应看到 `Cannot assign to` 或 `Property 'push' does not exist on type 'readonly ...[]'` 一类错误。

**坑**：这是编译期约束，不是运行时冻结；函数、`Date`、`Map`、`Set` 等内建对象通常要作为边界单独处理，否则会把方法签名也卷入递归。运行时防修改要用 `Object.freeze` 或不可变数据策略。

**检查**：你需要的是类型层面的不可改，还是运行时也不能改？递归只读是否已经明确排除了函数和内建对象边界？
