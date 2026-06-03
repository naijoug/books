# 品牌类型防止不同 ID 互相混用

**问题**：`userId`、`orderId`、`productId` 都是 `string`，TypeScript 不会阻止你把 `userId` 传给期望 `orderId` 的函数。怎么在编译期就捕获这类"同结构不同语义"的混用？

**要点**：

- 品牌类型（branded type）用一个唯一标记字段把名义上相同的类型区分开。
- 品牌构造函数负责把普通值"盖戳"为品牌值，是唯一允许绕过标记的入口。
- 业务函数只接受品牌类型；如果你拿到的是 `string`，必须先经过构造函数，这强制你在边界处确认语义。
- 不要手动构造品牌值的内部结构；所有品牌值都应通过构造函数产出。

**示例**：

```typescript
// 品牌标记：每个领域 ID 用一个独特的 symbol
interface UserIdBrand { readonly __userId: unique symbol }
interface OrderIdBrand { readonly __orderId: unique symbol }

type UserId = string & UserIdBrand;
type OrderId = string & OrderIdBrand;

// 品牌构造函数：唯一允许从 string 晋升为品牌值的入口
function asUserId(value: string): UserId {
  return value as UserId;
}

function asOrderId(value: string): OrderId {
  return value as OrderId;
}

// 业务函数只接受品牌类型
function getUserOrders(userId: UserId): string[] {
  return [`order-for-${userId}`];
}

function fulfillOrder(orderId: OrderId): string {
  return `fulfilled-${orderId}`;
}

// 编译通过：品牌类型匹配
const uid = asUserId("user-42");
const oid = asOrderId("order-99");

console.log(getUserOrders(uid));
console.log(fulfillOrder(oid));

// 编译失败：UserId 不能传给期望 OrderId 的参数
// Argument type 'UserId' is not assignable to parameter of type 'OrderId'.
// console.log(fulfillOrder(uid));
```

最小验证：把上面的代码保存为 `branded-types-prevent-id-mixing.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom branded-types-prevent-id-mixing.ts`；如果没有类型错误，说明品牌类型成功阻止了跨域 ID 混用。取消注释最后一行后应出现类型错误。

**坑**：品牌类型不是运行时隔离——`asUserId("x")` 在运行时还是普通字符串。它只在编译期防止混用，所以构造函数仍是你放置运行时校验（UUID 格式、前缀等）的好地方。

**检查**：每个领域 ID 至少回答三个问题：是否有自己的品牌标记？是否只能通过构造函数创建？传错 ID 时是否会在编译期而不是运行时报错？
