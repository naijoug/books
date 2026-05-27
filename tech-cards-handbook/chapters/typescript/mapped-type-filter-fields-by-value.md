# Mapped Type + 条件类型可以按值类型筛选字段

**问题**：如何从对象类型中只挑出 string 字段或 Date 字段？

**要点**：

- mapped type 遍历 key。
- key remapping 的 `as` 可以把不需要的 key 映射成 `never`。
- 适合构建表单字段、序列化字段和 API 工具类型。

**示例**：

```typescript
type Equal<A, B> =
  (<T>() => T extends A ? 1 : 2) extends
  (<T>() => T extends B ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};

type PickByAssignableValue<T, U> = {
  [K in keyof T as Extract<T[K], U> extends never ? never : K]: T[K];
};

interface User {
  id: number;
  name: string;
  email?: string;
  active: boolean;
  createdAt: Date;
  updatedAt: Date | null;
}

type UserStrings = PickByType<User, string>;
type UserDates = PickByType<User, Date>;
type UserDateLike = PickByAssignableValue<User, Date>;

type A = Expect<Equal<UserStrings, { name: string }>>;
type B = Expect<Equal<UserDates, { createdAt: Date }>>;
type C = Expect<Equal<UserDateLike, { createdAt: Date; updatedAt: Date | null }>>;
```

最小验证：把上面的代码保存为 `mapped-type-filter-fields-by-value.ts`，执行：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict mapped-type-filter-fields-by-value.ts
```

如果把 `type C` 的预期改成只包含 `{ createdAt: Date }`，编译器会报 `Type 'false' does not satisfy the constraint 'true'`，说明 `Date | null` 这种联合值类型需要用 `Extract` 或其他规则明确处理。

**坑**：类型筛选不能替代运行时筛选。JSON 进来之后仍然要校验真实数据；另外，`T[K] extends U` 不会选中 `Date | null` 这种“部分可赋值”的联合类型。

**检查**：这个类型是否和运行时代码保持一致？如果运行时会变，类型也要同步。字段是“完全 extends 某类型”还是“包含某类型分支”，要先写进类型断言。
