# 表单提交用 pending 锁和幂等键防重复写入

**问题**：

用户连续点击提交、移动端网络重试、浏览器恢复页面后重新发送请求，可能让同一个表单写入多次。前端只禁用按钮能减少重复点击，但不能防住网络层重放；后端只做唯一约束又会把正常重试变成难以恢复的报错。

**要点**：

- 前端用 `pending` 锁挡住同一表单实例里的重复点击，并在按钮上表达提交中状态。
- 每次“提交意图”生成一个幂等键，随请求发给服务端；服务端按用户、操作类型和幂等键去重。
- 同一次提交失败后允许用户用同一个幂等键重试，避免“其实已写入但响应丢失”时重复创建。
- 用户修改关键字段后，重新生成幂等键，因为这已经是新的写入意图。
- 幂等键不是安全凭证，仍要做鉴权、权限、业务校验和服务端唯一约束。

**示例**：

```tsx
type OrderInput = {
  skuId: string;
  quantity: number;
};

type CreateOrderResult =
  | { ok: true; orderId: string }
  | { ok: false; message: string; retryable: boolean };

declare function createOrder(input: OrderInput, idempotencyKey: string): Promise<CreateOrderResult>;

function newIdempotencyKey() {
  return crypto.randomUUID();
}

export function CreateOrderForm() {
  const [input, setInput] = useState<OrderInput>({ skuId: "book-001", quantity: 1 });
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState("");
  const idempotencyKeyRef = useRef<string>(newIdempotencyKey());

  function updateQuantity(quantity: number) {
    setInput((current) => ({ ...current, quantity }));
    idempotencyKeyRef.current = newIdempotencyKey();
    setMessage("");
  }

  async function submitOrder() {
    if (pending) {
      return;
    }

    setPending(true);
    setMessage("");
    const keyForThisAttempt = idempotencyKeyRef.current ?? newIdempotencyKey();
    idempotencyKeyRef.current = keyForThisAttempt;

    try {
      const result = await createOrder(input, keyForThisAttempt);
      if (result.ok) {
        setMessage(`订单已创建：${result.orderId}`);
        idempotencyKeyRef.current = newIdempotencyKey();
        return;
      }

      setMessage(result.message);
      if (!result.retryable) {
        idempotencyKeyRef.current = newIdempotencyKey();
      }
    } catch {
      setMessage("网络异常，可以安全重试本次提交");
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={(event: { preventDefault: () => void }) => {
      event.preventDefault();
      void submitOrder();
    }}>
      <label htmlFor="quantity">数量</label>
      <input
        id="quantity"
        type="number"
        min={1}
        value={input.quantity}
        onChange={(event: { target: { valueAsNumber: number } }) => updateQuantity(event.target.valueAsNumber)}
      />
      <button type="submit" disabled={pending} aria-busy={pending}>
        {pending ? "提交中..." : "创建订单"}
      </button>
      {message ? <p role="status">{message}</p> : null}
    </form>
  );
}
```

服务端也要保存幂等记录：同一用户、同一业务动作、同一 `idempotencyKey` 第一次成功后返回已创建资源；如果第一次仍在处理中，返回“处理中”或等待结果；如果请求体摘要不同，拒绝复用该 key。前端的 `pending` 只是体验优化，真正的重复写入边界必须在服务端闭合。

最小验证：把上面的代码保存为 `form-submit-idempotency-key-prevents-duplicate-writes.tsx`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx --lib es2020,dom form-submit-idempotency-key-prevents-duplicate-writes.tsx`。行为验证至少覆盖四条路径：连续点击只触发一次提交；网络异常后再次点击复用同一个幂等键；提交成功后生成新幂等键；修改数量后生成新幂等键。

**坑**：

- 只禁用按钮，不传幂等键；刷新、重放或移动端自动重试仍可能重复写入。
- 每次点击重试都生成新幂等键，导致“响应丢失后的安全重试”变成第二次创建。
- 把幂等键当成权限校验，忽略用户身份、请求摘要和业务唯一约束。
- 成功后不刷新幂等键，导致下一次真实提交被服务端当成重复请求。
- 所有业务共用同一个幂等命名空间，造成不同操作之间误判重复。

**检查**：

- 表单是否同时有前端 `pending` 锁和服务端幂等键？
- 失败后重试是复用同一个提交意图，还是错误地生成了新 key？
- 修改关键字段、成功提交、不可重试失败后，幂等键是否进入新生命周期？
- 服务端是否按用户、动作、key 和请求摘要判断重复，而不是只看一个裸 key？
