# 条件类型让类型根据输入变化

**问题**：如何让一个工具类型根据传入类型返回不同结果？

**要点**：

- 条件类型语法是 `T extends U ? X : Y`。
- 当 `T` 是联合类型时，条件类型默认会分发到每个成员。
- 常用于类型过滤、提取和转换。

**示例**：

```typescript
type Equal<A, B> =
  (<T>() => T extends A ? 1 : 2) extends
  (<T>() => T extends B ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

type IsString<T> = T extends string ? true : false;

type A = Expect<Equal<IsString<string>, true>>;
type B = Expect<Equal<IsString<number>, false>>;
type C = Expect<Equal<IsString<"hello">, true>>;

type OnlyStrings<T> = T extends string ? T : never;
type D = Expect<Equal<OnlyStrings<"a" | 1 | "b">, "a" | "b">>;

// 阻止联合类型分发：整个联合类型一起判断。
type IsAllString<T> = [T] extends [string] ? true : false;
type E = Expect<Equal<IsAllString<"a" | "b">, true>>;
type F = Expect<Equal<IsAllString<"a" | 1>, false>>;
```

可以把上面的代码保存为 `conditional-types-input-dependent.ts`，再运行：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict conditional-types-input-dependent.ts
```

如果把 `type F = ... false` 改成 `true`，编译器会报 `Type 'false' does not satisfy the constraint 'true'`，说明“阻止分发后整个联合一起判断”的规则被类型测试覆盖到了。

**坑**：联合类型分发有时会产生意外结果。需要阻止分发时，可以包一层元组：`[T] extends [U] ? X : Y`。不要只看鼠标悬浮里的展开结果，最好用 `Expect<Equal<...>>` 这种类型断言把预期固定下来。

**检查**：这个类型是否真的需要根据输入类型分支？是否已经用正向和反向的类型断言覆盖了分发与不分发两种情况？如果只是业务字段，普通接口更清晰。
