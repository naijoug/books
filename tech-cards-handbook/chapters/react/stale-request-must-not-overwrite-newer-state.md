# 旧请求不能覆盖更新状态

**问题**：用户快速切换筛选条件或详情页 ID 时，旧请求可能比新请求更晚返回。结果是界面明明已经切到新条件，却被上一轮响应覆盖，应该如何避免？

**要点**：

- 每次请求都绑定“本轮身份”：例如 `userId`、查询参数、递增 request id 或 `AbortController`。
- effect 依赖变化时清理上一轮请求；能取消就取消，不能取消也要用本轮身份忽略旧响应。
- 写入 state 前再确认请求仍然有效，不要只在发请求前检查一次。
- 错误也要区分：被主动取消的请求不是业务失败，不应展示错误 toast。
- 这类保护不替代缓存、分页或服务端幂等；它只保证 UI 不被过期响应回写。

**示例**：

```tsx
import { useEffect, useState } from "react";

type Profile = {
  id: string;
  name: string;
  plan: "free" | "pro";
};

type ProfileState =
  | { status: "loading" }
  | { status: "ready"; profile: Profile }
  | { status: "error"; message: string };

async function fetchProfile(userId: string, signal: AbortSignal): Promise<Profile> {
  const response = await fetch(`/api/users/${userId}`, { signal });
  if (!response.ok) {
    throw new Error(`load profile failed: ${response.status}`);
  }
  return (await response.json()) as Profile;
}

export function ProfilePanel({ userId }: { userId: string }) {
  const [state, setState] = useState<ProfileState>({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    setState({ status: "loading" });

    fetchProfile(userId, controller.signal)
      .then((profile) => {
        if (!active) return;
        setState({ status: "ready", profile });
      })
      .catch((error: unknown) => {
        if (!active || controller.signal.aborted) return;
        const message = error instanceof Error ? error.message : "unknown error";
        setState({ status: "error", message });
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [userId]);

  if (state.status === "loading") return <p>Loading profile…</p>;
  if (state.status === "error") return <p role="alert">{state.message}</p>;

  return (
    <section>
      <h2>{state.profile.name}</h2>
      <p>Plan: {state.profile.plan}</p>
    </section>
  );
}
```

这里 `userId` 变化会触发 cleanup：上一轮 `active` 被置为 `false`，同时请求被 `abort()`。即使底层请求没有及时中止，旧响应进入 `.then` 时也会被 `active` 挡住，不会覆盖新用户的状态。

**坑**：

- 只在请求开始时记录 `userId`，但响应回来后不再比对或不清理，旧响应仍能写入 state。
- 把 abort 当成业务错误展示给用户，造成快速切换时频繁闪错误提示。
- 依赖数组漏掉查询参数，导致请求根本没有随条件变化重跑。
- 同时维护 `loading`、`error`、`profile` 多个独立 state，旧响应可能只覆盖其中一部分；用联合类型更容易保持一致。
- 以为 `startTransition` 或 `useDeferredValue` 会自动处理网络过期；它们只影响渲染优先级，不取消请求。

**检查**：在浏览器 DevTools 里给接口加延迟，连续快速切换两个 `userId`。最后界面只能显示最后一次选择的用户；旧请求取消或晚到时，不应出现错误闪烁，也不能把旧用户资料写回。