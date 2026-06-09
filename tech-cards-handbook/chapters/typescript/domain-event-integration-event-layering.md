# Domain Event 与 Integration Event 要分层

**问题**：

领域事件记录业务内部已经发生的事实，常常跟聚合、事务和内部不变量绑定；Integration Event 面向其他系统或外部订阅者，是需要长期兼容的发布契约。如果把领域事件直接发布到消息队列，内部字段、命名和拆分方式会变成外部契约；如果让 Integration Event 反过来驱动领域模型，领域层又会被外部协议污染。

**要点**：

- Domain Event 放在业务层，描述内部事实，例如 `OrderPaidDomainEvent`，可以使用领域 ID、Date、内部枚举和事务上下文。
- Integration Event 放在发布边界，描述跨服务契约，例如 `OrderPaidIntegrationEventV1`，字段要稳定、可序列化、可版本化。
- 在事务完成后把 Domain Event 转换成 Integration Event；转换函数是边界 mapper，不承载业务决策。
- Integration Event 只携带外部消费者需要重建语义的字段，不泄漏内部风险分、成本价、审批轨迹等实现细节。
- 契约变化优先新增版本或可选字段，不让内部重构直接破坏消费者。

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
  riskBucket: "low" | "review" | "blocked";
};

type OrderPaidDomainEvent = {
  type: "OrderPaid";
  orderId: OrderId;
  buyerId: UserId;
  paidAt: Date;
  totalCents: number;
  currency: "CNY" | "USD";
  riskBucket: "low" | "review" | "blocked";
};

type OrderPaidIntegrationEventV1 = {
  type: "commerce.order_paid.v1";
  eventId: string;
  occurredAt: string;
  payload: {
    orderId: string;
    buyerId: string;
    amount: {
      cents: number;
      currency: "CNY" | "USD";
    };
  };
};

type PayOrderResult = {
  order: Order;
  domainEvents: OrderPaidDomainEvent[];
};

function payOrder(order: Order, paidAt: Date): PayOrderResult {
  if (order.status !== "pending") {
    throw new Error("only pending orders can be paid");
  }

  const paidOrder: Order = {
    ...order,
    status: "paid",
    paidAt,
  };

  return {
    order: paidOrder,
    domainEvents: [
      {
        type: "OrderPaid",
        orderId: paidOrder.id,
        buyerId: paidOrder.buyerId,
        paidAt,
        totalCents: paidOrder.totalCents,
        currency: paidOrder.currency,
        riskBucket: paidOrder.riskBucket,
      },
    ],
  };
}

function toOrderPaidIntegrationEventV1(
  domainEvent: OrderPaidDomainEvent,
  eventId: string,
): OrderPaidIntegrationEventV1 {
  return {
    type: "commerce.order_paid.v1",
    eventId,
    occurredAt: domainEvent.paidAt.toISOString(),
    payload: {
      orderId: domainEvent.orderId,
      buyerId: domainEvent.buyerId,
      amount: {
        cents: domainEvent.totalCents,
        currency: domainEvent.currency,
      },
    },
  };
}

const pendingOrder: Order = {
  id: "order_1" as OrderId,
  buyerId: "user_1" as UserId,
  totalCents: 12900,
  currency: "CNY",
  status: "pending",
  paidAt: null,
  riskBucket: "review",
};

const result = payOrder(pendingOrder, new Date("2026-06-09T02:00:00.000Z"));
const [domainEvent] = result.domainEvents;

if (domainEvent === undefined) {
  throw new Error("expected OrderPaid domain event");
}

const message = toOrderPaidIntegrationEventV1(domainEvent, "evt_1");

console.log(result.order.status, message.type, message.payload.amount.cents);
```

把代码块保存为 `domain-event-integration-event-layering.ts` 后，可用下面的命令做最小编译验证：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom domain-event-integration-event-layering.ts
```

这里 `OrderPaidDomainEvent` 可以保留 `OrderId`、`Date` 和 `riskBucket`，因为它服务于领域内部流程；`OrderPaidIntegrationEventV1` 则只发布稳定、可 JSON 序列化、消费者真正需要的字段，并用 `commerce.order_paid.v1` 显式标出外部契约版本。两个事件同名但不同层，转换发生在发布边界。

**坑**：

- 不要把 `OrderPaidDomainEvent` 原样 `JSON.stringify` 后发布到 MQ；内部字段会意外变成外部契约。
- 不要在领域层直接依赖 `commerce.order_paid.v1` 这类 topic 名或外部事件版本号。
- 不要为了满足某个消费者，把展示文案、跳转链接、分页参数塞回领域事件。
- 不要在 integration mapper 里重新判断订单能否支付；业务决策应在 use case / domain service 中完成。

**检查**：

- 是否能清楚指出每个事件是 domain event 还是 integration event。
- 发布到外部系统的事件是否有独立类型、版本和 mapper。
- 内部字段改名、领域事件拆分或聚合重构时，外部消费者是否不需要同步改。
- 新增消费者需求时，是通过契约演进处理，而不是让领域模型直接迎合某个消息订阅者。
