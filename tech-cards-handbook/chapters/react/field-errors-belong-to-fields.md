# 表单校验错误按字段归属

**问题**：

表单失败后只显示一句“提交失败”，用户不知道该改哪个输入；或者每个字段自己维护错误，提交时又有一份服务端错误，最后同一个错误在多个位置漂移。

**要点**：

- 字段级错误放在以字段名为 key 的结构里，例如 `Partial<Record<FieldName, string>>`。
- 全局错误只放跨字段、权限、网络、系统类问题，不要把邮箱格式错误塞进全局 toast。
- 客户端校验和服务端校验都归并到同一个 `fieldErrors`，UI 只从这一份状态渲染。
- 用户修改字段时，只清理该字段错误，避免把其他字段或全局错误误清掉。
- 字段错误要贴近输入渲染，并用 `aria-invalid`、`aria-describedby` 让辅助技术能关联错误文案。

**示例**：

```tsx
type FieldName = "email" | "password";

type LoginErrors = {
  fieldErrors: Partial<Record<FieldName, string>>;
  formError: string;
};

type LoginInput = Record<FieldName, string>;

const initialErrors: LoginErrors = { fieldErrors: {}, formError: "" };

type ServerLoginResult =
  | { ok: true }
  | { ok: false; formError?: string; fieldErrors?: LoginErrors["fieldErrors"] };

declare function login(input: LoginInput): Promise<ServerLoginResult>;

function validateLogin(input: LoginInput): LoginErrors["fieldErrors"] {
  const errors: LoginErrors["fieldErrors"] = {};
  if (!input.email.includes("@")) {
    errors.email = "请输入有效邮箱";
  }
  if (input.password.length < 8) {
    errors.password = "密码至少 8 位";
  }
  return errors;
}

export function LoginForm() {
  const [input, setInput] = useState<LoginInput>({ email: "", password: "" });
  const [errors, setErrors] = useState<LoginErrors>(initialErrors);
  const [submitting, setSubmitting] = useState(false);

  function updateField(name: FieldName, value: string) {
    setInput((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({
      formError: current.formError,
      fieldErrors: { ...current.fieldErrors, [name]: undefined },
    }));
  }

  async function handleSubmit() {
    const fieldErrors = validateLogin(input);
    if (Object.keys(fieldErrors).length > 0) {
      setErrors({ fieldErrors, formError: "请修正表单错误" });
      return;
    }

    setSubmitting(true);
    setErrors(initialErrors);
    try {
      const result = await login(input);
      if (!result.ok) {
        setErrors({
          fieldErrors: result.fieldErrors ?? {},
          formError: result.formError ?? "登录失败，请稍后重试",
        });
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={(event: { preventDefault: () => void }) => {
      event.preventDefault();
      void handleSubmit();
    }}>
      <label htmlFor="email">邮箱</label>
      <input
        id="email"
        value={input.email}
        aria-invalid={Boolean(errors.fieldErrors.email)}
        aria-describedby={errors.fieldErrors.email ? "email-error" : undefined}
        onChange={(event: { target: { value: string } }) => updateField("email", event.target.value)}
      />
      {errors.fieldErrors.email ? <p id="email-error" role="alert">{errors.fieldErrors.email}</p> : null}

      <label htmlFor="password">密码</label>
      <input
        id="password"
        type="password"
        value={input.password}
        aria-invalid={Boolean(errors.fieldErrors.password)}
        aria-describedby={errors.fieldErrors.password ? "password-error" : undefined}
        onChange={(event: { target: { value: string } }) => updateField("password", event.target.value)}
      />
      {errors.fieldErrors.password ? <p id="password-error" role="alert">{errors.fieldErrors.password}</p> : null}

      <button type="submit" disabled={submitting}>{submitting ? "登录中..." : "登录"}</button>
      {errors.formError ? <p role="status">{errors.formError}</p> : null}
    </form>
  );
}
```

最小验证：把上面的代码保存为 `field-errors-belong-to-fields.tsx`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx --lib es2020,dom field-errors-belong-to-fields.tsx`。行为验证至少覆盖四条路径：邮箱格式错误显示在邮箱下方；密码长度错误显示在密码下方；服务端返回字段错误能落到对应输入；修改邮箱只清理邮箱错误，不影响密码错误。

**坑**：

- 只维护一个 `errorMessage`，导致用户不知道该修改哪个字段。
- 每个输入组件内部各自存错误，提交结果回来后无法统一回填。
- 修改任意字段时清空所有错误，让用户失去其他字段的修正提示。
- 把网络错误、权限错误和字段格式错误都塞进同一个 toast，既不可访问也不可定位。
- 字段名用散落字符串，字段重命名时错误 key 和输入 name 不同步。

**检查**：

- 表单 state 是否明确区分 `fieldErrors` 和 `formError`？
- 每个字段错误是否渲染在对应输入附近，并被 `aria-describedby` 关联？
- 客户端和服务端校验是否写入同一个错误结构？
- 字段变化时是否只清理该字段错误，而不是清空整张表单的错误？
