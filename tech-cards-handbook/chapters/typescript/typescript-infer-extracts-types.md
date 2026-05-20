# `infer` 用于从类型里提取信息

**问题**：如何从函数、数组、Promise 中拿到内部类型？

**要点**：

- `infer` 只能出现在条件类型中。
- 它让类型系统在匹配时保存某个局部类型。
- 常见用途是写工具类型。

**示例**：

```typescript
type AwaitedValue<T> = T extends Promise<infer U> ? U : T;

type UserResponse = Promise<{ id: string; name: string }>;
type User = AwaitedValue<UserResponse>;
```

**坑**：类型工具过度嵌套会让错误信息很难读。业务代码里优先简单清晰。

**检查**：这个类型工具是否能被至少两个地方复用？不能就先别抽。
