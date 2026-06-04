# 请求缓存去重相同读取

## 问题

同一个页面里，列表、侧栏和详情卡片可能在同一时间读取同一份资源。如果每个组件都在自己的 `useEffect` 里直接 `fetch`，用户一次导航会打出多份相同请求：加载更慢、后端压力更大，也更容易出现“后返回的旧数据覆盖新数据”。

## 要点

- 读取请求要先定义稳定的 cache key，例如 `user:${userId}`，不要用临时对象或函数作为 key。
- 同一个 key 的进行中请求应该复用同一个 Promise，而不是重复发起网络请求。
- 缓存不仅要存成功值，也要处理失败：失败后通常删除进行中记录，允许下一次重试。
- 组件卸载时只取消本组件的写入，不要随意中止被多个消费者共享的请求。
- 写入状态前仍要检查本组件是否有效；请求去重不能替代 stale response 防护。

## 示例

```tsx
import { useEffect, useState } from 'react';

type User = { id: string; name: string; plan: 'free' | 'pro' };
type RemoteUser =
  | { status: 'idle' | 'loading' }
  | { status: 'success'; user: User }
  | { status: 'error'; message: string };

const userRequestCache = new Map<string, Promise<User>>();

async function fetchUser(userId: string): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) {
    throw new Error(`failed to load user ${userId}`);
  }
  return response.json() as Promise<User>;
}

function loadUserOnce(userId: string): Promise<User> {
  const key = `user:${userId}`;
  const cached = userRequestCache.get(key);
  if (cached) {
    return cached;
  }

  const request = fetchUser(userId).catch((error: unknown) => {
    userRequestCache.delete(key);
    throw error;
  });
  userRequestCache.set(key, request);
  return request;
}

export function UserSummary({ userId }: { userId: string }) {
  const [state, setState] = useState<RemoteUser>({ status: 'idle' });

  useEffect(() => {
    let active = true;
    setState({ status: 'loading' });

    loadUserOnce(userId)
      .then((user) => {
        if (active) {
          setState({ status: 'success', user });
        }
      })
      .catch((error: unknown) => {
        if (active) {
          const message = error instanceof Error ? error.message : 'unknown error';
          setState({ status: 'error', message });
        }
      });

    return () => {
      active = false;
    };
  }, [userId]);

  if (state.status === 'loading' || state.status === 'idle') {
    return <p>Loading user...</p>;
  }
  if (state.status === 'error') {
    return <p role="alert">{state.message}</p>;
  }
  if (state.status === 'success') {
    return <p>{state.user.name} · {state.user.plan}</p>;
  }
  return null;
}
```

## 坑

- 用 `JSON.stringify(options)` 当 key 时要小心字段顺序和非序列化值；生产代码最好显式拼出 key。
- 把失败 Promise 永久留在缓存里，会让用户永远无法重试。
- 在共享缓存层随便 `abort()` 请求，可能会让另一个仍在挂载的组件一起失败。
- 缓存会带来失效问题；写操作成功后要主动清理相关 key，或给缓存增加 TTL / 版本号。

## 检查

- 页面上两个组件同时读取同一 `userId` 时，Network 面板里只出现一条请求。
- 失败后点击重试会重新发请求，而不是立刻复用旧失败。
- 组件卸载后 Promise resolve 不会触发 state update。
- 切换到另一个 `userId` 后，旧响应不会覆盖新用户状态。
