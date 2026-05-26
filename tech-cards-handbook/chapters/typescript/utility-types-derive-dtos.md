# 工具类型从领域模型派生 DTO

**问题**：

同一个业务对象在不同边界会有不同形态：创建请求没有 `id`，更新请求只允许部分字段，列表项不需要详情字段。若每个 DTO 都手写一遍字段，领域模型变化时很容易漏改。

**要点**：

- 把完整领域模型作为源头，再用 `Pick`、`Omit`、`Partial`、`Required` 派生边界类型。
- `Pick<T, K>` 只保留需要暴露或提交的字段。
- `Omit<T, K>` 去掉由系统生成或不允许外部传入的字段。
- `Partial<T>` 适合 PATCH/表单草稿，表示字段可以缺省；不要把它当成完整对象。
- `Required<T>` 适合在校验完成后，把可选字段提升成内部必填类型。

**示例**：

```typescript
type User = {
  id: string;
  name: string;
  email: string;
  role: "admin" | "member";
  avatarUrl?: string;
  createdAt: string;
  updatedAt: string;
};

type UserListItem = Pick<User, "id" | "name" | "avatarUrl">;

type CreateUserRequest = Omit<
  User,
  "id" | "createdAt" | "updatedAt" | "avatarUrl"
> & {
  avatarUrl?: string;
};

type UpdateUserRequest = Partial<
  Pick<User, "name" | "email" | "role" | "avatarUrl">
>;

type PersistedUser = Required<User>;

function toListItem(user: User): UserListItem {
  return {
    id: user.id,
    name: user.name,
    avatarUrl: user.avatarUrl,
  };
}

function updateUser(id: string, patch: UpdateUserRequest) {
  return fetch(`/api/users/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}
```

**坑**：

- 不要为了省事把 API 入参写成 `Partial<User>`：这会把 `id`、`createdAt` 等不该由外部修改的字段也放进候选范围。
- `Omit<User, "id">` 不等于安全的创建请求；还要检查系统字段、只读字段和后端实际接受的字段。
- 工具类型只在编译期工作；外部 JSON 仍然需要运行时校验。
- 派生层级太深时可读性会下降，复杂 DTO 可以先拆出中间别名。

**检查**：

- 是否能从类型名看出它属于哪个边界：`CreateUserRequest`、`UpdateUserRequest`、`UserListItem`。
- 更新请求是否只允许业务上可修改的字段，而不是直接 `Partial<User>`。
- 系统生成字段是否被 `Omit` 掉。
- 领域模型新增字段后，相关 DTO 是否会通过 `Pick`/`Omit` 暴露出需要复核的编译错误。
