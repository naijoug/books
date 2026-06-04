# 缓存过期要有 TTL 或版本号

## 问题

请求缓存命中以后，页面会更快，但也更容易展示过期数据。只靠“写操作后失效”不够：别的用户、后台任务、Webhook 或定时同步也可能改变资源。没有过期策略的缓存会把旧 Promise 一直复用；过期策略太粗，又会让每次渲染都重新请求。

## 要点

- TTL 负责“最多相信多久”：适合列表、统计、搜索结果这类允许短暂陈旧的数据。
- 版本号负责“是否仍是同一份资源”：适合详情页、配置、权限等需要精确一致性的读取。
- 缓存条目不要只存 Promise；同时存 `expiresAt`、`version`、`value` 或读取结果，才能判断是否可复用。
- TTL 到期后再重新读取，不要在每次 render 中因为时间变化直接 setState。
- 写操作成功后仍要局部失效；TTL/版本号是兜底，不是 mutation 后刷新的替代品。

## 示例

```tsx
import { useEffect, useState } from 'react';

type Project = { id: string; name: string; version: number; updatedAt: string };
type ProjectState =
  | { status: 'loading' }
  | { status: 'success'; project: Project; stale: boolean }
  | { status: 'error'; message: string };

type CacheEntry<T> = {
  value?: T;
  promise?: Promise<T>;
  expiresAt: number;
  version?: number;
};

const projectCache = new Map<string, CacheEntry<Project>>();
const PROJECT_TTL_MS = 30_000;

function projectKey(projectId: string): string {
  return `project:${projectId}`;
}

async function fetchProject(projectId: string): Promise<Project> {
  const response = await fetch(`/api/projects/${projectId}`);
  if (!response.ok) {
    throw new Error('failed to load project');
  }
  return response.json() as Promise<Project>;
}

function readProject(projectId: string, now = Date.now()): Promise<Project> {
  const key = projectKey(projectId);
  const cached = projectCache.get(key);

  if (cached?.value && cached.expiresAt > now) {
    return Promise.resolve(cached.value);
  }
  if (cached?.promise && cached.expiresAt > now) {
    return cached.promise;
  }

  const request = fetchProject(projectId)
    .then((project) => {
      projectCache.set(key, {
        value: project,
        expiresAt: Date.now() + PROJECT_TTL_MS,
        version: project.version,
      });
      return project;
    })
    .catch((error: unknown) => {
      projectCache.delete(key);
      throw error;
    });

  projectCache.set(key, {
    value: cached?.value,
    promise: request,
    expiresAt: now + PROJECT_TTL_MS,
    version: cached?.version,
  });
  return request;
}

function invalidateProject(projectId: string, nextVersion?: number): void {
  const key = projectKey(projectId);
  const cached = projectCache.get(key);
  if (!cached) {
    return;
  }

  if (nextVersion === undefined || cached.version === undefined || nextVersion > cached.version) {
    projectCache.delete(key);
  }
}

export function ProjectHeader({ projectId }: { projectId: string }) {
  const [state, setState] = useState<ProjectState>({ status: 'loading' });

  useEffect(() => {
    let active = true;
    const cached = projectCache.get(projectKey(projectId));
    if (cached?.value) {
      setState({ status: 'success', project: cached.value, stale: cached.expiresAt <= Date.now() });
    } else {
      setState({ status: 'loading' });
    }

    readProject(projectId)
      .then((project) => {
        if (active) {
          setState({ status: 'success', project, stale: false });
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
  }, [projectId]);

  if (state.status === 'loading') {
    return <p>Loading project...</p>;
  }
  if (state.status === 'error') {
    return <p role="alert">{state.message}</p>;
  }

  return (
    <header>
      <h2>{state.project.name}</h2>
      {state.stale ? <small>Showing cached data while refreshing.</small> : null}
    </header>
  );
}

void invalidateProject;
```

## 坑

- 把缓存写成永久 `Map<string, Promise<T>>`，导致后台更新后页面一直读旧结果。
- TTL 太短，用户每次切换标签都重新请求；TTL 太长，产品已经不能接受陈旧窗口。
- 用本地时间判断服务端版本，但没有保存资源版本号或 `updatedAt`，无法判断写后事件是否更新。
- TTL 到期时立刻清空 UI，造成闪烁；更好的方式是展示旧值并在后台刷新。
- 以为 TTL 可以替代写后失效，保存成功后仍等 30 秒才刷新列表或详情。

## 检查

- 相同 project 在 TTL 内重复进入页面不会重复发请求。
- TTL 到期后会重新读取；刷新期间可展示旧值和 stale 提示。
- mutation 或订阅事件带来更高版本号时，对应详情缓存会被删除或刷新。
- 请求失败会删除进行中缓存，下一次进入页面可以重试。
- TTL 数值能用产品语义解释：哪些数据允许陈旧 5 秒、30 秒或必须立即刷新。
