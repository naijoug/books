# `useActionState` 把表单提交状态收拢到 action

**问题**：

表单提交常被拆成多个互相漂移的状态：`isSubmitting`、`error`、`successMessage`、字段校验结果和按钮禁用逻辑各写一处。AI 生成代码尤其容易只处理成功路径，漏掉重复提交、服务端校验失败和提交后的状态回填。

**要点**：

- `useActionState` 适合把“提交动作 + 提交结果状态 + pending”放在一个边界里维护。
- action 接收上一轮 state 和本次 payload（表单里通常是 `FormData`），返回下一轮 state。
- state 应表达用户可见结果：字段错误、全局错误、成功消息，而不是只放一个布尔值。
- `pending` 只表示这次 action 是否正在执行；按钮禁用、loading 文案应从它派生。
- action 里不要吞掉服务端校验结果；把可恢复错误转换成 state，把真正意外错误交给错误边界或监控。

**示例**：

```tsx
import { useActionState } from "react";

type ProfileFormState = {
  status: "idle" | "success" | "error";
  message: string;
  fieldErrors: Partial<Record<"name" | "email", string>>;
};

const initialState: ProfileFormState = {
  status: "idle",
  message: "",
  fieldErrors: {},
};

type SaveProfileResult =
  | { ok: true; message: string }
  | { ok: false; message: string; fieldErrors?: ProfileFormState["fieldErrors"] };

declare function saveProfile(input: { name: string; email: string }): Promise<SaveProfileResult>;

async function submitProfile(
  _previousState: ProfileFormState,
  formData: FormData,
): Promise<ProfileFormState> {
  const name = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();

  const fieldErrors: ProfileFormState["fieldErrors"] = {};
  if (name.length === 0) {
    fieldErrors.name = "请输入姓名";
  }
  if (!email.includes("@")) {
    fieldErrors.email = "请输入有效邮箱";
  }
  if (Object.keys(fieldErrors).length > 0) {
    return { status: "error", message: "请修正表单错误", fieldErrors };
  }

  const result = await saveProfile({ name, email });
  if (!result.ok) {
    return {
      status: "error",
      message: result.message,
      fieldErrors: result.fieldErrors ?? {},
    };
  }

  return { status: "success", message: result.message, fieldErrors: {} };
}

export function ProfileForm() {
  const [state, formAction, pending] = useActionState(submitProfile, initialState);

  return (
    <form action={formAction}>
      <label>
        姓名
        <input name="name" aria-invalid={Boolean(state.fieldErrors.name)} />
      </label>
      {state.fieldErrors.name ? <p role="alert">{state.fieldErrors.name}</p> : null}

      <label>
        邮箱
        <input name="email" type="email" aria-invalid={Boolean(state.fieldErrors.email)} />
      </label>
      {state.fieldErrors.email ? <p role="alert">{state.fieldErrors.email}</p> : null}

      <button type="submit" disabled={pending}>
        {pending ? "保存中..." : "保存"}
      </button>
      {state.message ? <p role="status">{state.message}</p> : null}
    </form>
  );
}
```

最小验证：把上面的代码保存为 `useactionstate-keeps-form-submission-state.tsx`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx --lib es2020,dom useactionstate-keeps-form-submission-state.tsx`。行为验证至少覆盖三条路径：空姓名返回字段错误；服务端返回校验失败时错误进入 state；成功保存后按钮 pending 结束且显示成功消息。

**坑**：

- action 只返回 `true/false`，导致 UI 不知道该显示哪个字段错误。
- 同时维护 `pending` 和手写 `isSubmitting`，两个状态在失败或快速重复提交时不一致。
- 在 action 中直接读 DOM 或全局变量，而不是从 `FormData` 构造输入。
- catch 后统一返回“系统错误”，把服务端的可恢复校验信息丢掉。
- 在按钮、错误文案、成功文案里重复拼装提交状态，后续新增字段时容易漏改。

**检查**：

- action 的返回 state 是否覆盖 idle、success、error 以及字段错误？
- UI 是否只从 `state` 和 `pending` 派生，而不是额外复制提交状态？
- 服务端校验失败和客户端校验失败是否都能落到用户可见位置？
- 是否有测试或手工步骤覆盖重复点击、失败后修改再提交、成功后再次提交？
