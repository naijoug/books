# `useFormStatus` 只放在表单内部读取提交状态

**问题**：

React 表单 action 让提交逻辑可以直接挂在 `<form>` 上，但按钮、提示文案和防重复提交常常仍散落在父组件里。很多实现会在父组件手写 `isSubmitting`，或者把 `useFormStatus` 放到表单同级组件中，结果读不到当前表单的提交状态。

**要点**：

- `useFormStatus` 从 `react-dom` 导入，用来读取最近一次表单提交的 `pending`、`data`、`method` 和 `action`。
- 调用它的组件必须渲染在目标 `<form>` 内部；放在表单外层或同级组件，拿不到这个表单的上下文状态。
- 提交按钮、局部 loading、提交中的辅助文案适合拆成表单内部子组件，让它们直接从 `useFormStatus` 派生状态。
- 表单的业务结果仍应由 action 返回值、`useActionState` 或父级数据刷新表达；`useFormStatus` 不替代领域状态。
- 不要把 `pending` 复制到本地 state；否则失败、重试、并发表单时很容易和真实提交状态不同步。

**示例**：

```tsx
import { useFormStatus } from "react-dom";

type SubscribeResult =
  | { ok: true; message: string }
  | { ok: false; message: string };

declare function subscribe(email: string): Promise<SubscribeResult>;
declare function refreshSubscribers(): void;

async function submitSubscription(formData: FormData): Promise<void> {
  const email = String(formData.get("email") ?? "").trim();
  if (!email.includes("@")) {
    throw new Error("请输入有效邮箱");
  }

  const result = await subscribe(email);
  if (!result.ok) {
    throw new Error(result.message);
  }

  refreshSubscribers();
}

function SubmitButton() {
  const { pending, data, method } = useFormStatus();
  const submittedEmail = String(data?.get("email") ?? "");

  return (
    <div>
      <button type="submit" disabled={pending}>
        {pending ? "订阅中..." : "订阅"}
      </button>
      {pending ? (
        <p role="status">
          正在通过 {method ?? "POST"} 提交{submittedEmail ? `：${submittedEmail}` : ""}
        </p>
      ) : null}
    </div>
  );
}

export function NewsletterForm() {
  return (
    <form action={submitSubscription}>
      <label>
        邮箱
        <input name="email" type="email" required />
      </label>
      <SubmitButton />
    </form>
  );
}
```

最小验证：把上面的代码保存为 `useformstatus-belongs-inside-form.tsx`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx --lib es2020,dom useformstatus-belongs-inside-form.tsx`。行为验证至少覆盖：点击提交后按钮禁用并显示 pending 文案；同一页面两个表单同时存在时，只更新当前表单内按钮；提交失败后 pending 能恢复。

**坑**：

- 在包含 `<form>` 的父组件里调用 `useFormStatus`，再把 `pending` 作为 prop 传给按钮；这时 Hook 不在表单内部，状态通常不是你以为的那一个。
- 用全局 loading 控制多个表单，导致 A 表单提交时 B 表单也被禁用。
- 把 `data` 当作最终业务数据保存；它只是本次提交的 `FormData` 快照。
- 只用 `pending` 展示成功/失败；成功和失败应由 action 结果或数据刷新表达。
- 为了显示提交中邮箱而读取输入 DOM；直接从 `data?.get("email")` 派生即可。

**检查**：

- 调用 `useFormStatus` 的组件是否实际渲染在目标 `<form>` 内部？
- 页面有多个表单时，pending 是否只影响当前表单的按钮和文案？
- 业务成功、字段错误、系统错误是否有独立表达，而不是塞进 `useFormStatus`？
- 是否有测试或手工步骤覆盖快速重复点击、失败重试、同页多表单并存？