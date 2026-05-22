# 模板字面量类型约束字符串格式

**问题**：事件名、接口路径、权限 key 这类字符串常常有固定格式。如果都写成 `string`，拼错只能等到运行时或人工 review 才发现。

**要点**：

- 模板字面量类型可以把多个字符串联合类型拼成新的字符串格式。
- 适合约束有限组合：事件名、CSS token、权限点、路由片段、i18n key。
- 和泛型、`keyof` 组合时，可以让“字符串协议”和对象结构保持同步。
- 不适合生成过大的组合；组合数量会膨胀，影响可读性和类型检查速度。

**示例**：

```ts
type Entity = "user" | "order" | "invoice";
type Action = "created" | "updated" | "deleted";

type DomainEvent = `${Entity}.${Action}`;

function publish(event: DomainEvent, payload: unknown) {
  console.log(event, payload);
}

publish("user.created", { id: "u1" });
publish("invoice.deleted", { id: "i1" });

// publish("users.created", {}); // ❌ Entity 拼错
// publish("user.create", {});   // ❌ Action 拼错
```

还可以让事件名来自对象 key：

```ts
type WatchSource = {
  firstName: string;
  age: number;
};

type ChangedEvent<T> = `${Extract<keyof T, string>}Changed`;

function onChanged<T>(event: ChangedEvent<T>, handler: () => void) {
  handler();
}

onChanged<WatchSource>("firstNameChanged", () => {});
onChanged<WatchSource>("ageChanged", () => {});

// onChanged<WatchSource>("nameChanged", () => {}); // ❌ 不存在 name 字段
```

**坑**：不要把模板字面量类型当成运行时校验。它只能约束 TypeScript 编译期可见的字符串；从 URL、JSON、环境变量等边界进来的值仍然需要运行时解析和校验。

**检查**：当一组字符串有固定前缀、后缀或分隔符时，先问两个问题：组合是否有限？是否能从已有联合类型或对象 key 推导？如果答案都是“是”，就用模板字面量类型替代裸 `string`。
