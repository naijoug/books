# 表单 action 返回结构要让错误可恢复

**问题**：

服务端 action 失败后只抛异常或只返回一句 `failed`，前端无法判断是字段错误、表单级错误、权限问题还是成功后的跳转提示。结果是用户看到一个笼统 toast，改完字段后旧错误还在，或者可恢复的校验失败被 Error Boundary 当成系统崩溃处理。

**要点**：

- action 的返回值要围绕“用户下一步能做什么”设计，而不是围绕 HTTP/数据库异常设计。
- 用可判别联合类型区分 `idle`、`success`、`field_error`、`form_error` 等状态，避免多个布尔值互相打架。
- 字段错误放进稳定的 `fieldErrors` map；表单级错误放进 `message`；真正不可恢复的异常再抛给错误边界或监控。
- 成功结果也要清空旧错误，并返回用户可见的成功消息或下一步状态。
- action 里做输入归一化和服务端校验；客户端校验只能改善体验，不能替代服务端 contract。

**示例**：

```tsx
import { useActionState } from "react";

type SignupField = "email" | "password";

type SignupState =
  | { status: "idle"; message: ""; fieldErrors: Partial<Record<SignupField, string>> }
  | { status: "success"; message: string; fieldErrors: Partial<Record<SignupField, string>> }
  | { status: "field_error"; message: string; fieldErrors: Partial<Record<SignupField, string>> }
  | { status: "form_error"; message: string; fieldErrors: Partial<Record<SignupField, string>> };

type CreateAccountResult =
  | { ok: true; welcomeMessage: string }
  | { ok: false; reason: "email_taken" | "weak_password" | "rate_limited" };

const initialSignupState: SignupState = { status: "idle", message: "", fieldErrors: {} };

declare function createAccount(input: { email: string; password: string }): Promise<CreateAccountResult>;

function validateSignup(input: { email: string; password: string }): Partial<Record<SignupField, string>> {
  const errors: Partial<Record<SignupField, string>> = {};
  if (!input.email.includes("@")) {
    errors.email = "请输入有效邮箱";
  }
  if (input.password.length < 12) {
    errors.password = "密码至少 12 位";
  }
  return errors;
}

async function submitSignup(_previous: SignupState, formData: FormData): Promise<SignupState> {
  const input = {
    email: String(formData.get("email") ?? "").trim().toLowerCase(),
    password: String(formData.get("password") ?? ""),
  };

  const fieldErrors = validateSignup(input);
  if (Object.keys(fieldErrors).length > 0) {
    return { status: "field_error", message: "请修正标出的字段", fieldErrors };
  }

  const result = await createAccount(input);
  if (result.ok) {
    return { status: "success", message: result.welcomeMessage, fieldErrors: {} };
  }

  if (result.reason === "email_taken") {
    return {
      status: "field_error",
      message: "请更换邮箱或直接登录",
      fieldErrors: { email: "这个邮箱已经注册" },
    };
  }

  if (result.reason === "weak_password") {
    return {
      status: "field_error",
      message: "请使用更强的密码",
      fieldErrors: { password: "密码强度不足" },
    };
  }

  return { status: "form_error", message: "请求过于频繁，请稍后再试", fieldErrors: {} };
}

export function SignupForm() {
  const [state, formAction, pending] = useActionState(submitSignup, initialSignupState);

  return (
    <form action={formAction}>
      <label htmlFor="signup-email">邮箱</label>
      <input
        id="signup-email"
        name="email"
        type="email"
        aria-invalid={Boolean(state.fieldErrors.email)}
        aria-describedby={state.fieldErrors.email ? "signup-email-error" : undefined}
      />
      {state.fieldErrors.email ? <p id="signup-email-error" role="alert">{state.fieldErrors.email}</p> : null}

      <label htmlFor="signup-password">密码</label>
      <input
        id="signup-password"
        name="password"
        type="password"
        aria-invalid={Boolean(state.fieldErrors.password)}
        aria-describedby={state.fieldErrors.password ? "signup-password-error" : undefined}
      />
      {state.fieldErrors.password ? <p id="signup-password-error" role="alert">{state.fieldErrors.password}</p> : null}

      <button type="submit" disabled={pending}>{pending ? "创建中..." : "创建账号"}</button>
      {state.message ? <p role={state.status === "field_error" ? "alert" : "status"}>{state.message}</p> : null}
    </form>
  );
}
```

最小验证：把上面的代码保存为 `server-action-result-contract-keeps-form-recoverable.tsx`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx --lib es2020,dom server-action-result-contract-keeps-form-recoverable.tsx`。行为验证至少覆盖四条路径：本地字段校验失败；服务端返回邮箱已占用；服务端返回限流表单级错误；成功后旧字段错误被清空且显示成功消息。

**坑**：

- action 直接 `throw new Error("邮箱已注册")`，让可恢复字段错误进入错误边界。
- 只返回 `{ ok: false }`，UI 只能猜测显示什么文案、清理哪些字段。
- 成功时没有清空旧 `fieldErrors`，导致保存成功后仍显示上一轮错误。
- 服务端返回结构和前端 state 各写一套，字段名稍微改动就失配。
- 把限流、权限、字段校验都放进同一个字段错误，用户会误以为改输入就能恢复。

**检查**：

- action 返回类型是否是显式联合类型，而不是散落的可选字段和布尔值？
- 字段错误、表单级错误、成功消息是否有固定归属？
- 可恢复错误是否返回 state，不可恢复错误才抛出？
- 成功路径是否清空旧错误，并给出用户下一步可见反馈？
