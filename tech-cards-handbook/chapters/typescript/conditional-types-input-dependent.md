# 条件类型让类型根据输入变化

**问题**：如何让一个工具类型根据传入类型返回不同结果？

**要点**：

- 条件类型语法是 `T extends U ? X : Y`。
- 当 `T` 是联合类型时，条件类型默认会分发到每个成员。
- 常用于类型过滤、提取和转换。

**示例**：

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false
type C = IsString<"hello">; // true
```

**坑**：联合类型分发有时会产生意外结果。需要阻止分发时，可以包一层元组：`[T] extends [U] ? X : Y`。

**检查**：这个类型是否真的需要根据输入类型分支？如果只是业务字段，普通接口更清晰。
