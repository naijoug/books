# 写操作成功后要失效相关缓存

## 问题

请求缓存能去重相同读取，但它不会自动知道哪一次写操作改变了哪些资源。用户保存资料、创建订单或切换状态后，如果仍复用旧 cache key，界面会继续展示过期数据；如果粗暴清空所有缓存，又会制造不必要的重新加载和闪烁。

## 要点

- 先把读取 key 设计成可枚举的资源边界，例如 `user:${id}`、`user-list:${teamId}`。
- 写操作成功后，主动删除受影响的 key：通常包括详情 key、列表 key、统计 key。
- 不要在写操作发起时就清缓存；失败时会让界面失去可回退的旧数据。
- 失效策略要尽量局部：只删确实被写操作影响的资源，而不是清空整个缓存。
- 失效后可以立即重新读取，也可以让下一次挂载/刷新自然触发读取；关键是不要继续复用旧 Promise 或旧值。

## 示例

```tsx
import { useEffect, useState } from 'react';

type User = { id: string; name: string; role: 'viewer' | 'editor' };
type RemoteUser =
  | { status: 'loading' }
  | { status: 'success'; user: User }
  | { status: 'error'; message: string };

const userCache = new Map<string, Promise<User>>();

function userKey(userId: string): string {
  return `user:${userId}`;
}

function teamUsersKey(teamId: string): string {
  return `team-users:${teamId}`;
}

async function fetchUser(userId: string): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) {
    throw new Error('failed to load user');
  }
  return response.json() as Promise<User>;
}

function loadUser(userId: string): Promise<User> {
  const key = userKey(userId);
  const cached = userCache.get(key);
  if (cached) {
    return cached;
  }

  const request = fetchUser(userId).catch((error: unknown) => {
    userCache.delete(key);
    throw error;
  });
  userCache.set(key, request);
  return request;
}

function invalidateUserAfterSave(userId: string, teamId: string): void {
  userCache.delete(userKey(userId));
  userCache.delete(teamUsersKey(teamId));
}

async function saveUserRole(userId: string, role: User['role']): Promise<void> {
  const response = await fetch(`/api/users/${userId}/role`, {
    method: 'POST',
    body: JSON.stringify({ role }),
    headers: { 'content-type': 'application/json' },
  });
  if (!response.ok) {
    throw new Error('failed to save role');
  }
}

export function UserRoleEditor({ userId, teamId }: { userId: string; teamId: string }) {
  const [state, setState] = useState<RemoteUser>({ status: 'loading' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    setState({ status: 'loading' });

    loadUser(userId)
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

  async function changeRole(role: User['role']) {
    setSaving(true);
    try {
      await saveUserRole(userId, role);
      invalidateUserAfterSave(userId, teamId);
      const freshUser = await loadUser(userId);
      setState({ status: 'success', user: freshUser });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'unknown error';
      setState({ status: 'error', message });
    } finally {
      setSaving(false);
    }
  }

  if (state.status === 'loading') {
    return <p>Loading user...</p>;
  }
  if (state.status === 'error') {
    return <p role="alert">{state.message}</p>;
  }

  return (
    <section>
      <p>{state.user.name} · {state.user.role}</p>
      <button disabled={saving} onClick={() => void changeRole('editor')}>
        Make editor
      </button>
    </section>
  );
}
```

## 坑

- 只失效详情 key，忘记失效列表 key，会出现“详情已更新，列表仍旧”的不一致。
- 写操作还没成功就清缓存，失败后用户看到空白或被迫重新加载。
- 用模糊前缀批量删除时没有边界，例如把 `user:1` 和 `user:10` 一起删掉。
- 失效后不重新读取，也不等待下一次读取触发，导致当前页面继续展示旧 state。

## 检查

- 保存成功后，详情页下一次读取不会复用保存前的 Promise。
- 受影响的列表或统计入口也会刷新，而不是只刷新当前详情组件。
- 保存失败时旧数据仍可显示，并能给出错误提示。
- Network 面板里能看到失效后的重新读取；没有无关资源被成批重拉。
