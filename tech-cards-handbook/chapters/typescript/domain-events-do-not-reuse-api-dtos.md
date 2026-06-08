# 领域事件不要复用 API DTO

**问题**：

API DTO 面向当前调用方的读写契约，字段会跟着页面、接口版本、权限和展示需要变化。领域事件面向系统内部或异步订阅者，表达“业务上已经发生的事实”。如果把 API DTO 直接当事件 payload，事件会混入展示字段、可选输入字段和权限裁剪结果；后续 API 改版时，消息消费者也会被无关改动拖着变。

**要点**：

- API DTO 是边界请求/响应格式；领域事件是业务事实记录，二者的变化原因不同。
- 事件名用过去式表达已经发生的事实，例如 `OrderPaid`、`ProductPublished`、`InvoiceVoided`。
- 事件 payload 只放订阅者重建业务语义所需的稳定字段，不放按钮状态、展示文案、分页字段或临时表单字段。
- 从领域对象或业务命令显式构造事件，使用 `toXxxEvent` / `recordXxxEvent` 这样的 mapper 固化边界。
- 对外发布到消息队列时，可以再把领域事件转换成 integration event DTO；不要反过来让 HTTP DTO 驱动领域事件。

**示例**：

```typescript
type Brand<T, Name extends string> = T & { readonly __brand: Name };

type OrderId = Brand<string, "OrderId">;
type UserId = Brand<string, "UserId">;

type Order = {
  id: OrderId;
  buyerId: UserId;
  totalCents: number;
  currency: "CNY" | "USD";
  status: "pending" | "paid" | "cancelled";
  paidAt: Date | null;
  internalRiskScore: number;
};

type PayOrderResponseDto = {
  orderId: string;
  status: "paid";
  paidAt: string;
  displayTotal: string;
  receiptUrl: string;
};

type OrderPaidEvent = {
  type: "OrderPaid";
  eventId: string;
  occurredAt: string;
  orderId: string;
  buyerId: string;
  amountCents: number;
  currency: "CNY" | "USD";
};

function payOrder(order: Order, now: Date): Order {
  if (order.status !== "pending") {
    throw new Error("only pending orders can be paid");
  }

  return {
    ...order,
    status: "paid",
    paidAt: now,
  };
}

function toPayOrderResponseDto(order: Order): PayOrderResponseDto {
  if (order.status !== "paid" || order.paidAt === null) {
    throw new Error("paid order response requires paid order");
  }

  return {
    orderId: order.id,
    status: "paid",
    paidAt: order.paidAt.toISOString(),
    displayTotal: `${order.currency} ${(order.totalCents / 100).toFixed(2)}`,
    receiptUrl: `/orders/${order.id}/receipt`,
  };
}

function toOrderPaidEvent(order: Order, eventId: string, occurredAt: Date): OrderPaidEvent {
  if (order.status !== "paid") {
    throw new Error("OrderPaid event requires paid order");
  }

  return {
    type: "OrderPaid",
    eventId,
    occurredAt: occurredAt.toISOString(),
    orderId: order.id,
    buyerId: order.buyerId,
    amountCents: order.totalCents,
    currency: order.currency,
  };
}

const pendingOrder: Order = {
  id: "order_1" as OrderId,
  buyerId: "user_1" as UserId,
  totalCents: 12900,
  currency: "CNY",
  status: "pending",
  paidAt: null,
  internalRiskScore: 42,
};

const paidOrder = payOrder(pendingOrder, new Date("2026-06-09T00:00:00.000Z"));
const responseDto = toPayOrderResponseDto(paidOrder);
const orderPaidEvent = toOrderPaidEvent(paidOrder, "evt_1", new Date("2026-06-09T00:00:01.000Z"));

console.log(responseDto.receiptUrl, orderPaidEvent.type, orderPaidEvent.amountCents);
```

把代码块保存为 `domain-events-do-not-reuse-api-dtos.ts` 后，可用下面的命令做最小编译验证：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom domain-events-do-not-reuse-api-dtos.ts
```

注意 `PayOrderResponseDto` 有 `displayTotal` 和 `receiptUrl`，这是面向 HTTP 调用方的展示/跳转契约；`OrderPaidEvent` 则保留 `buyerId`、金额、币种和发生时间，表达可被账务、通知、分析等订阅者复用的业务事实。两者都来自 `Order`，但不能互相复用。

**坑**：

- 不要把 `CreateOrderDto`、`PayOrderResponseDto` 这类 HTTP 类型直接 publish 到消息队列；接口字段一改，消费者就会被迫跟着改。
- 不要在领域事件里放 `displayName`、`href`、`buttonDisabled`、`pageSize` 等展示或请求控制字段。
- 不要让事件 payload 偷偷包含 `internalRiskScore`、成本价、权限标记等内部字段；事件也可能跨服务、跨团队流动。
- 不要把事件当命令使用：`OrderPaid` 表示已经发生，不能要求订阅者再决定“是否支付”。

**检查**：

- 事件类型名是否用过去式描述业务事实，而不是 API 动作或页面操作。
- 每个事件是否有独立类型和 mapper，而不是 `type OrderPaidEvent = PayOrderResponseDto`。
- payload 字段是否能解释业务事实，同时不包含 UI 状态、分页参数和敏感内部字段。
- API DTO 改字段名、增加展示字段或做版本兼容时，事件消费者是否不需要同步改动。
