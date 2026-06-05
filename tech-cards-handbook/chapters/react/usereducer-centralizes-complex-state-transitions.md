# useReducer 把复杂状态转移集中到可测试的纯函数

## 问题

当 `useState` 管理的对象有多个互相依赖的字段，或者下一个状态取决于当前状态和动作类型时，散落在各处的 `setState` 调用容易遗漏分支、产生不可能的状态组合。

```tsx
function Checkout() {
  const [step, setStep] = useState<'shipping' | 'payment' | 'review'>('shipping');
  const [address, setAddress] = useState('');
  const [shippingMethod, setShippingMethod] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [error, setError] = useState('');

  // 多处 setState 散落在不同 handler，容易遗漏或顺序依赖
  function handleAddressSubmit() {
    if (!address.trim()) {
      setError('Address is required');
      return;
    }
    setError('');
    setStep('payment');
  }

  function handleShippingChange(method: string) {
    setShippingMethod(method);
    // 忘记重置 payment？
    // 忘记清空 error？
  }
}
```

## 解决

把状态和所有可能的变更路径集中到一个 reducer 纯函数里。组件只负责分发动作，状态如何变更全部由 reducer 决定。

```tsx
interface CheckoutState {
  step: 'shipping' | 'payment' | 'review';
  address: string;
  shippingMethod: string;
  paymentMethod: string;
  error: string;
}

type CheckoutAction =
  | { type: 'SET_ADDRESS'; address: string }
  | { type: 'SELECT_SHIPPING'; method: string }
  | { type: 'SELECT_PAYMENT'; method: string }
  | { type: 'NEXT_STEP' }
  | { type: 'BACK' }
  | { type: 'CLEAR_ERROR' };

function checkoutReducer(state: CheckoutState, action: CheckoutAction): CheckoutState {
  switch (action.type) {
    case 'SET_ADDRESS':
      return { ...state, address: action.address, error: '' };
    case 'SELECT_SHIPPING':
      // 选择新配送方式时，重置支付方式，避免不一致组合
      return { ...state, shippingMethod: action.method, paymentMethod: '', error: '' };
    case 'SELECT_PAYMENT':
      return { ...state, paymentMethod: action.method, error: '' };
    case 'NEXT_STEP':
      if (state.step === 'shipping' && !state.address.trim()) {
        return { ...state, error: 'Address is required' };
      }
      if (state.step === 'shipping' && !state.shippingMethod) {
        return { ...state, error: 'Shipping method is required' };
      }
      if (state.step === 'payment' && !state.paymentMethod) {
        return { ...state, error: 'Payment method is required' };
      }
      return {
        ...state,
        step: state.step === 'shipping' ? 'payment'
          : state.step === 'payment' ? 'review'
          : state.step,
        error: '',
      };
    case 'BACK':
      return {
        ...state,
        step: state.step === 'review' ? 'payment'
          : state.step === 'payment' ? 'shipping'
          : state.step,
        error: '',
      };
    case 'CLEAR_ERROR':
      return { ...state, error: '' };
    default:
      return state;
  }
}

const initialState: CheckoutState = {
  step: 'shipping',
  address: '',
  shippingMethod: '',
  paymentMethod: '',
  error: '',
};

function Checkout() {
  const [state, dispatch] = useReducer(checkoutReducer, initialState);

  // 组件只分发动作，不直接修改状态
  return (
    <form onSubmit={(e: { preventDefault(): void }) => { e.preventDefault(); dispatch({ type: 'NEXT_STEP' }); }}>
      {state.step === 'shipping' && (
        <>
          <input value={state.address} onChange={(e: { target: { value: string } }) => dispatch({ type: 'SET_ADDRESS', address: e.target.value })} />
          <select value={state.shippingMethod} onChange={(e: { target: { value: string } }) => dispatch({ type: 'SELECT_SHIPPING', method: e.target.value })}>
            <option value="">Select shipping</option>
            <option value="standard">Standard</option>
            <option value="express">Express</option>
          </select>
        </>
      )}
      {state.step === 'payment' && (
        <select value={state.paymentMethod} onChange={(e: { target: { value: string } }) => dispatch({ type: 'SELECT_PAYMENT', method: e.target.value })}>
          <option value="">Select payment</option>
          <option value="card">Card</option>
          <option value="cod">Cash on delivery</option>
        </select>
      )}
      {state.error && <p role="alert">{state.error}</p>}
      <button type="button" onClick={() => dispatch({ type: 'BACK' })}>Back</button>
      <button type="submit">Continue</button>
    </form>
  );
}
```

## 要点

- **所有分支集中可见**：reducer 的 switch/case 就是状态机的完整转移表，不可能状态组合一目了然。
- **可独立测试**：reducer 是纯函数，不需要渲染组件就能覆盖所有分支。
- **用 discriminated union 定义 action**：TypeScript 会强制每个 case 处理对应 payload，漏写字段会报错。
- **不要用 useReducer 替代 useState 管理简单独立值**：只有一个布尔开关或一个字符串，用 `useState` 更直接。
- **不要在 reducer 里发请求或读 ref**：reducer 必须是纯函数，副作用放在 effect 或事件 handler 里。

## 检查方式

- 在 reducer 函数上方列出所有 action type 和每个 action 要更新的字段，确认没有遗漏的分支。
- 给 reducer 写独立的单元测试，覆盖正常路径、无效输入回退和状态重置。
- 检查组件中是否还有直接 `setState` 残留；全部改为 `dispatch`。
