# API DTO 版本演进不要回灌领域模型

**问题**：

API 一旦被外部调用方依赖，就会出现 v1 / v2 并存、字段兼容、旧字段别名和迁移窗口。如果为了兼容旧接口，把 `display_name`、`fullName`、`avatarUrl`、`avatar_url` 等版本字段都塞回领域模型，业务层会被传输层历史包袱污染，后续每次改接口都变成全域重构。

**要点**：

- 领域模型表达当前业务事实；API DTO 表达某个版本的外部契约。
- 版本兼容应停留在 controller / adapter / mapper 边界，不要让领域模型保存多个接口版本字段。
- 新旧 DTO 可以共存，但都映射到同一个领域模型或领域命令。
- 输出版本化 DTO 时，用 `toXxxDtoV1`、`toXxxDtoV2` 等显式函数隔离兼容逻辑。
- 输入旧版本 DTO 时，在 `fromXxxDtoV1` 中做字段归一化，再交给业务用例。

**示例**：

```typescript
type Brand<T, Name extends string> = T & { readonly __brand: Name };

type UserId = Brand<string, "UserId">;

type UserProfile = {
  id: UserId;
  displayName: string;
  avatarImageUrl: string | null;
  bio: string;
  updatedAt: Date;
};

type UserProfileDtoV1 = {
  id: string;
  display_name: string;
  avatar_url: string | null;
};

type UserProfileDtoV2 = {
  id: string;
  displayName: string;
  avatarImageUrl: string | null;
  bio: string;
  updatedAt: string;
};

type UpdateProfileDtoV1 = {
  display_name: string;
  avatar_url?: string | null;
};

type UpdateProfileDtoV2 = {
  displayName: string;
  avatarImageUrl?: string | null;
  bio?: string;
};

type UpdateProfileCommand = {
  userId: UserId;
  displayName: string;
  avatarImageUrl: string | null;
  bio: string | null;
};

function normalizeOptionalUrl(value: string | null | undefined): string | null {
  if (value === undefined || value === null) {
    return null;
  }

  const trimmed = value.trim();
  return trimmed.length === 0 ? null : trimmed;
}

function toUserProfileDtoV1(profile: UserProfile): UserProfileDtoV1 {
  return {
    id: profile.id,
    display_name: profile.displayName,
    avatar_url: profile.avatarImageUrl,
  };
}

function toUserProfileDtoV2(profile: UserProfile): UserProfileDtoV2 {
  return {
    id: profile.id,
    displayName: profile.displayName,
    avatarImageUrl: profile.avatarImageUrl,
    bio: profile.bio,
    updatedAt: profile.updatedAt.toISOString(),
  };
}

function fromUpdateProfileDtoV1(
  userId: UserId,
  dto: UpdateProfileDtoV1,
): UpdateProfileCommand {
  return {
    userId,
    displayName: dto.display_name.trim(),
    avatarImageUrl: normalizeOptionalUrl(dto.avatar_url),
    bio: null,
  };
}

function fromUpdateProfileDtoV2(
  userId: UserId,
  dto: UpdateProfileDtoV2,
): UpdateProfileCommand {
  return {
    userId,
    displayName: dto.displayName.trim(),
    avatarImageUrl: normalizeOptionalUrl(dto.avatarImageUrl),
    bio: dto.bio?.trim() ?? null,
  };
}

const profile: UserProfile = {
  id: "user_1" as UserId,
  displayName: "Ada Lovelace",
  avatarImageUrl: "https://example.com/ada.png",
  bio: "Writes programs before computers are common.",
  updatedAt: new Date("2026-06-01T00:00:00.000Z"),
};

const dtoV1 = toUserProfileDtoV1(profile);
const dtoV2 = toUserProfileDtoV2(profile);
const commandFromV1 = fromUpdateProfileDtoV1(profile.id, {
  display_name: " Ada ",
  avatar_url: "",
});
const commandFromV2 = fromUpdateProfileDtoV2(profile.id, {
  displayName: " Ada Lovelace ",
  bio: " mathematician ",
});

console.log(dtoV1.display_name, dtoV2.updatedAt, commandFromV1.avatarImageUrl, commandFromV2.bio);
```

把代码块保存为 `api-dto-version-does-not-backflow-domain-model.ts` 后，可用下面的命令做最小编译验证：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom api-dto-version-does-not-backflow-domain-model.ts
```

注意 `UserProfile` 里只有当前领域真正关心的 `displayName`、`avatarImageUrl`、`bio` 和 `updatedAt`，没有 `display_name`、`avatar_url` 这类旧接口字段。兼容逻辑被限制在 v1 / v2 mapper 里。

**坑**：

- 不要为了兼容 v1，把旧字段名加入领域模型；旧字段名属于 API 契约，不属于业务事实。
- 不要在业务用例里写 `if (apiVersion === "v1")`；版本分支应在 adapter 层被消化。
- 不要让 `Partial<DtoV1 & DtoV2>` 变成“万能输入”；它会让必填字段、弃用字段和默认值都失去边界。
- 不要删除旧 DTO 时只改类型；还要确认外部调用方、文档、测试和发布策略已经完成迁移。

**检查**：

- 每个公开 API 版本是否有独立 DTO 类型和 mapper，而不是直接改领域模型。
- 旧版本字段是否只出现在 adapter / mapper / API 文档中，不进入领域层。
- 新字段默认值、旧字段别名和弃用策略是否集中在边界函数里。
- 领域模型重命名字段时，是否不会被迫同步改所有外部 API 版本。
