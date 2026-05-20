# 深度只读类型要谨慎处理对象边界

**问题**：如何让嵌套配置对象在编译期不可修改？

**要点**：

- `readonly` 只作用于当前层。
- 递归 mapped type 可以实现深度只读。
- 函数、Date、Map 等特殊对象不适合简单递归。

**示例**：

```typescript
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object
    ? DeepReadonly<T[K]>
    : T[K];
};

interface Config {
  database: {
    host: string;
    port: number;
  };
}

const config: DeepReadonly<Config> = {
  database: { host: "localhost", port: 5432 },
};

// config.database.host = "prod"; // 编译错误
```

**坑**：这是编译期约束，不是运行时冻结。运行时防修改要用 `Object.freeze` 或不可变数据策略。

**检查**：你需要的是类型层面的不可改，还是运行时也不能改？
