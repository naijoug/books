# `useOptimistic` 只覆盖过渡中的乐观视图

**问题**：

产品希望用户提交后立刻看到结果，于是代码常把“临时记录”直接塞进真实列表，再在请求成功或失败时手写替换、删除、回滚。这样不仅容易遗漏失败路径，还会让多个并发提交互相覆盖，最后 UI、缓存和服务端数据三者不一致。

**要点**：

- `useOptimistic` 从 `react` 导入，用真实状态和一个纯 `updateFn` 生成“过渡中的乐观状态”。
- 它适合配合 form action、server action 或任意 async mutation：真实数据仍由服务端响应、缓存刷新或父组件 props 驱动。
- `updateFn(currentState, optimisticValue)` 必须是纯函数；不要在里面发请求、改外部变量或生成随机 ID。
- 乐观值要带临时身份、展示文案和 pending 标记，避免和真实记录混淆。
- 请求失败时不要再手动修补乐观列表；让真实状态保持不变，并用错误提示解释失败即可。

**示例**：

```tsx
import { useOptimistic, useState } from "react";

type Comment = {
  id: string;
  body: string;
  status: "saved" | "sending";
};

type OptimisticComment = {
  clientId: string;
  body: string;
};

declare function createComment(body: string): Promise<Comment>;
declare function reportError(message: string): void;

export function CommentComposer({ initialComments }: { initialComments: Comment[] }) {
  const [comments, setComments] = useState(initialComments);
  const [draft, setDraft] = useState("");
  const [optimisticComments, addOptimisticComment] = useOptimistic(
    comments,
    (currentComments: Comment[], optimistic: OptimisticComment) => [
      {
        id: optimistic.clientId,
        body: optimistic.body,
        status: "sending" as const,
      },
      ...currentComments,
    ],
  );

  async function submitComment(formData: FormData): Promise<void> {
    const body = String(formData.get("body") ?? "").trim();
    if (!body) {
      return;
    }

    const clientId = `client-${Date.now()}`;
    addOptimisticComment({ clientId, body });
    setDraft("");

    try {
      const saved = await createComment(body);
      setComments((currentComments) => [saved, ...currentComments]);
    } catch (error) {
      reportError(error instanceof Error ? error.message : "评论提交失败");
    }
  }

  return (
    <section>
      <form action={submitComment}>
        <label>
          评论
          <textarea
            name="body"
            value={draft}
            onChange={(event: { target: { value: string } }) => setDraft(event.target.value)}
          />
        </label>
        <button type="submit">发送</button>
      </form>

      <ul>
        {optimisticComments.map((comment) => (
          <li key={comment.id} aria-busy={comment.status === "sending"}>
            {comment.body}
            {comment.status === "sending" ? "（发送中）" : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
```

最小验证：把上面的代码保存为 `useoptimistic-overlays-transient-state.tsx`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --jsx react-jsx --lib es2020,dom useoptimistic-overlays-transient-state.tsx`。行为验证至少覆盖：提交后立即出现 pending 评论；请求成功后 pending 评论被真实记录替代；请求失败后真实列表不被污染且出现错误提示；连续快速提交时每条 pending 记录都有独立身份。

**坑**：

- 把乐观记录直接写进真实 state，然后失败时再靠数组过滤回滚；并发提交时很容易删错。
- 在 `updateFn` 里调用 `Date.now()`、发请求或修改外部缓存；`updateFn` 应只根据输入计算下一个视图。
- 乐观记录没有 pending/temporary 标记，用户无法区分“已保存”和“正在提交”。
- 请求成功后同时保留乐观记录和真实记录，造成重复项；真实状态应由成功响应或刷新结果驱动。
- 只验证成功路径，忽略失败、重试、连续提交和乱序返回。

**检查**：

- 真实状态和乐观状态是否分层表达，而不是互相污染？
- `updateFn` 是否是纯函数，并且只依赖 `currentState` 与 `optimisticValue`？
- 乐观值是否包含稳定临时身份，列表 key 是否不会与真实 ID 冲突？
- 成功、失败、连续提交、乱序返回是否都有测试或手工验证步骤？
