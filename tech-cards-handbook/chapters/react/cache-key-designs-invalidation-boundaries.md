# 缓存 key 设计决定失效边界

## 问题

请求缓存不是一个 `Map` 就结束了。真正难的是：什么算“同一个读取”？写操作成功后应该删哪些 key？如果 key 只写成 `/api/users`，不同团队、筛选条件、分页游标会互相污染；如果 key 里塞入临时对象，又会导致相同查询无法命中缓存。

## 要点

- key 必须由稳定、可序列化的资源身份组成：资源类型、主 ID、筛选条件、排序、分页游标。
- 读列表时不要只用端点路径；把会影响结果集的条件全部放进 key。
- 写操作成功后按资源边界失效：详情 key、受影响的列表 key、统计 key，而不是清空全局缓存。
- key 生成函数集中维护，避免组件里手写字符串导致遗漏或拼写不一致。
- 分页 key 要区分“同一个列表的第几页”和“整个列表资源”；列表级失效可以用 prefix 或索引表批量找到相关页。

## 示例

```tsx
import { useEffect, useMemo, useState } from 'react';

type Sort = 'newest' | 'oldest';
type User = { id: string; name: string; teamId: string };
type Page = { users: User[]; nextCursor: string | null };
type RemotePage =
  | { status: 'loading' }
  | { status: 'success'; page: Page }
  | { status: 'error'; message: string };

type UserListQuery = {
  teamId: string;
  search: string;
  sort: Sort;
  cursor: string | null;
};

const pageCache = new Map<string, Promise<Page>>();

function normalizeSearch(search: string): string {
  return search.trim().toLowerCase();
}

function userDetailKey(userId: string): string {
  return `user:${userId}`;
}

function userListPrefix(teamId: string): string {
  return `team-users:${teamId}:`;
}

function userListKey(query: UserListQuery): string {
  const search = encodeURIComponent(normalizeSearch(query.search));
  const cursor = query.cursor ?? 'first';
  return `${userListPrefix(query.teamId)}search=${search}:sort=${query.sort}:cursor=${cursor}`;
}

async function fetchUsers(query: UserListQuery): Promise<Page> {
  const params = new URLSearchParams({
    search: normalizeSearch(query.search),
    sort: query.sort,
  });
  if (query.cursor) {
    params.set('cursor', query.cursor);
  }

  const response = await fetch(`/api/teams/${query.teamId}/users?${params.toString()}`);
  if (!response.ok) {
    throw new Error('failed to load users');
  }
  return response.json() as Promise<Page>;
}

function loadUserPage(query: UserListQuery): Promise<Page> {
  const key = userListKey(query);
  const cached = pageCache.get(key);
  if (cached) {
    return cached;
  }

  const request = fetchUsers(query).catch((error: unknown) => {
    pageCache.delete(key);
    throw error;
  });
  pageCache.set(key, request);
  return request;
}

function invalidateTeamUserLists(teamId: string): void {
  const prefix = userListPrefix(teamId);
  for (const key of Array.from(pageCache.keys())) {
    if (key.startsWith(prefix)) {
      pageCache.delete(key);
    }
  }
}

function invalidateAfterUserSave(user: User): void {
  pageCache.delete(userDetailKey(user.id));
  invalidateTeamUserLists(user.teamId);
}

export function TeamUserList({ teamId, search, sort }: { teamId: string; search: string; sort: Sort }) {
  const [state, setState] = useState<RemotePage>({ status: 'loading' });
  const query = useMemo<UserListQuery>(
    () => ({ teamId, search, sort, cursor: null }),
    [teamId, search, sort],
  );

  useEffect(() => {
    let active = true;
    setState({ status: 'loading' });

    loadUserPage(query)
      .then((page) => {
        if (active) {
          setState({ status: 'success', page });
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
  }, [query]);

  if (state.status === 'loading') {
    return <p>Loading users...</p>;
  }
  if (state.status === 'error') {
    return <p role="alert">{state.message}</p>;
  }

  return (
    <ul>
      {state.page.users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}

void invalidateAfterUserSave;
```

## 坑

- 只用端点路径做 key，导致不同筛选、排序或分页结果互相复用。
- 把未归一化的搜索词直接放进 key，`"Alice"`、`" alice "`、`"ALICE"` 变成三份缓存。
- 写操作只删详情 key，不删相关列表 key，列表页仍展示旧结果。
- 每个组件都手写 key 字符串，后续改参数时漏改某个入口。
- 失效列表时用没有边界的字符串匹配，把其他团队或其他资源一起删掉。

## 检查

- Network 面板中，相同 team/search/sort/cursor 只触发一次进行中请求。
- 改变 search、sort 或 cursor 会生成不同 key，不会复用旧结果集。
- 保存用户成功后，详情和所在团队的用户列表都会重新读取。
- key 生成函数有单一入口；新增筛选条件时只需要改类型和 key 函数。
- 批量失效有明确 prefix 边界，不会误删无关资源。
