# Strict Mode 双次调用暴露副作用

**问题**：为什么开发环境里开启 `<StrictMode>` 后，组件的 effect 看起来会执行两次？这是不是 React 的 bug？

**要点**：

- React Strict Mode 会在开发环境额外执行一次 setup → cleanup → setup，用来暴露 effect 清理不完整、渲染阶段有副作用、订阅重复注册等问题。
- 不要用“全局变量挡住第二次执行”来掩盖问题；正确做法是让 effect 可重复 setup，并且 cleanup 能完整撤销上一轮 setup。
- 如果 effect 里发起读取请求，参数变化或组件卸载时要取消/忽略旧请求；如果 effect 里写入数据，要确认写操作是否真的应由组件挂载触发。
- 生产环境不会因为 Strict Mode 多跑这一轮开发检查，但代码应该按“重复挂载也安全”的标准设计。

**示例**：

```tsx
import { useEffect, useState } from "react";

type Profile = { name: string };

async function fetchProfile(userId: string, signal: AbortSignal): Promise<Profile> {
  const response = await fetch(`/api/users/${userId}`, { signal });
  if (!response.ok) {
    throw new Error("failed to load profile");
  }
  return (await response.json()) as Profile;
}

function ProfilePanel({ userId }: { userId: string }) {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetchProfile(userId, controller.signal)
      .then((nextProfile) => {
        setProfile(nextProfile);
        setError(null);
      })
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setError("加载失败，请稍后重试");
      });

    return () => controller.abort();
  }, [userId]);

  if (error) return <p>{error}</p>;
  return <p>{profile?.name ?? "Loading..."}</p>;
}
```

**坑**：看到开发环境重复请求时，不要马上移除 `<StrictMode>`；先检查 effect 是否缺 cleanup、是否把事件上报/扣费/创建订单这类不可重复写操作放进了挂载 effect。

**检查**：在 Strict Mode 下刷新页面，观察每个 effect 是否满足“第一次 setup 的资源能被 cleanup 完整释放，第二次 setup 不依赖第一次残留状态”；如果做不到，生产环境遇到快速切换路由、Suspense 重试或组件重挂载时也可能出错。
