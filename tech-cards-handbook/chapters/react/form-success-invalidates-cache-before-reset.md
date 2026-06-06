# 表单成功后先处理一致性，再重置输入

**问题**：

表单提交成功后，代码常立刻 `reset()` 或清空本地 state，却忘记让列表、详情、计数和缓存看到这次写入。用户得到“保存成功”的提示，但返回上一页仍是旧数据；或者成功消息还没被消费，表单已经被清空，用户无法确认刚才提交了什么。

**要点**：

- 把“写入成功”“缓存/路由失效”“本地视图更新”“表单重置”拆成顺序明确的步骤。
- 只有服务端确认成功后才失效缓存；字段错误和表单级错误不能触发重置。
- 重置输入前，先让成功消息、跳转、列表刷新或详情更新至少完成一个可见反馈。
- 如果成功后留在当前页，重置表单要同时清理旧字段错误、幂等键和乐观临时项。
- 如果成功后跳转或关闭弹窗，可以不手写 reset，但仍要保证目标页面不会复用旧缓存。

**示例**：

```tsx
import { useActionState, useState } from "react";

type Todo = { id: string; title: string };
type CreateTodoState =
  | { status: "idle"; message: ""; fieldErrors: Partial<Record<"title", string>> }
  | { status: "success"; message: string; created: Todo; fieldErrors: Partial<Record<"title", string>> }
  | { status: "field_error"; message: string; fieldErrors: Partial<Record<"title", string>> }
  | { status: "form_error"; message: string; fieldErrors: Partial<Record<"title", string>> };

const initialCreateTodoState: CreateTodoState = {
  status: "idle",
  message: "",
  fieldErrors: {},
};

const todoListCache = new Map<string, Promise<Todo[]>>();

declare function createTodo(input: { title: string }): Promise<{ ok: true; todo: Todo } | { ok: false; reason: "empty" | "blocked" }>;

function invalidateTodoList(): void {
  todoListCache.delete("todos:all");
}

async function submitTodo(_previous: CreateTodoState, formData: FormData): Promise<CreateTodoState> {
  const title = String(formData.get("title") ?? "").trim();
  if (title.length === 0) {
    return { status: "field_error", message: "请填写标题", fieldErrors: { title: "标题不能为空" } };
  }

  const result = await createTodo({ title });
  if (result.ok) {
    return { status: "success", message: "已创建待办", created: result.todo, fieldErrors: {} };
  }
  if (result.reason === "empty") {
    return { status: "field_error", message: "请填写标题", fieldErrors: { title: "标题不能为空" } };
  }
  return { status: "form_error", message: "当前账号暂时不能创建待办", fieldErrors: {} };
}

export function CreateTodoForm() {
  const [state, formAction, pending] = useActionState(submitTodo, initialCreateTodoState);
  const [formVersion, setFormVersion] = useState(0);
  const [localTodos, setLocalTodos] = useState<Todo[]>([]);

  function consumeSuccess(): void {
    if (state.status !== "success") {
      return;
    }

    invalidateTodoList();
    setLocalTodos((current) => [state.created, ...current]);
    setFormVersion((version) => version + 1);
  }

  return (
    <section>
      <form key={formVersion} action={formAction}>
        <label htmlFor="todo-title">标题</label>
        <input
          id="todo-title"
          name="title"
          aria-invalid={Boolean(state.fieldErrors.title)}
          aria-describedby={state.fieldErrors.title ? "todo-title-error" : undefined}
        />
        {state.fieldErrors.title ? <p id="todo-title-error" role="alert">{state.fieldErrors.title}</p> : null}

        <button type="submit" disabled={pending}>{pending ? "创建中..." : "创建"}</button>
        {state.message ? <p role={state.status === "field_error" ? "alert" : "status"}>{state.message}</p> : null}
      </form>

      {state.status === "success" ? <button onClick={consumeSuccess}>确认并继续添加</button> : null}
      <ul>{localTodos.map((todo) => <li key={todo.id}>{todo.title}</li>)}</ul>
    </section>
  );
}
```

最小验证：把上面的代码保存为 `form-success-invalidates-cache-before-reset.tsx`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx --lib es2020,dom form-success-invalidates-cache-before-reset.tsx`。行为验证至少覆盖四条路径：字段错误时不重置；成功后列表缓存被失效；成功消息可见后再清空输入；连续创建两条记录时不会复用上一轮字段错误或临时视图。

**坑**：

- 成功回调第一行就清空输入，结果用户看不到服务端实际接受了什么。
- 只重置当前表单，不失效列表/详情缓存，导致页面其他区域继续显示旧数据。
- 字段错误也触发 reset，用户必须重新输入原本正确的字段。
- 乐观插入成功后又整页重新拉取，造成列表闪烁或重复出现同一条记录。
- 重置表单但没有刷新幂等键，下一次提交被服务端误判为上一轮重试。

**检查**：

- 成功路径是否显式列出：服务端确认、缓存失效或本地合并、用户反馈、表单重置？
- 失败路径是否保留用户输入和字段错误，而不是清空一切？
- 重置前后是否同步清理旧错误、乐观项和幂等键？
- 切到列表页或详情页时，是否能看到刚才写入的最新结果？
