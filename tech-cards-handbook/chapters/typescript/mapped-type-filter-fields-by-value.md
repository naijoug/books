# Mapped Type + 条件类型可以按值类型筛选字段

**问题**：如何从对象类型中只挑出 string 字段或 Date 字段？

**要点**：

- mapped type 遍历 key。
- key remapping 的 `as` 可以把不需要的 key 映射成 `never`。
- 适合构建表单字段、序列化字段和 API 工具类型。

**示例**：

```typescript
type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};

interface User {
  id: number;
  name: string;
  active: boolean;
  createdAt: Date;
}

type UserStrings = PickByType<User, string>; // { name: string }
type UserDates = PickByType<User, Date>;     // { createdAt: Date }
```

**坑**：类型筛选不能替代运行时筛选。JSON 进来之后仍然要校验真实数据。

**检查**：这个类型是否和运行时代码保持一致？如果运行时会变，类型也要同步。
