# 弃用 DTO 字段要有迁移窗口和测试

**问题**：

外部 API 字段不能像内部变量一样说删就删。一个字段被移动、重命名或替换后，老客户端、Webhook 消费者、自动化脚本和第三方集成可能还在读取旧字段。如果只在类型里删除字段，编译能通过，但线上会变成静默破坏；如果为了兼容又把旧字段塞回领域模型，领域层会背上接口历史包袱。

**要点**：

- 弃用字段属于 API 契约演进问题，不属于领域模型问题。
- 先新增新字段，再保留旧字段一段迁移窗口，并在 DTO mapper 中同时输出。
- 旧字段应标记 `@deprecated`，但仍由测试锁住，直到明确删除版本。
- 输入兼容逻辑集中在 adapter / mapper：优先读新字段，缺失时才回退旧字段。
- 删除旧字段前要确认客户端迁移、文档、监控和契约测试都已完成。

**示例**：

```typescript
type Brand<T, Name extends string> = T & { readonly __brand: Name };

type AccountId = Brand<string, "AccountId">;

type Account = {
  id: AccountId;
  displayName: string;
  avatarImageUrl: string | null;
  updatedAt: Date;
};

type AccountDtoV2 = {
  id: string;
  displayName: string;
  avatarImageUrl: string | null;
  /** @deprecated Use avatarImageUrl. Kept until 2026-09-30 for mobile clients. */
  avatarUrl: string | null;
  updatedAt: string;
};

type UpdateAccountDtoV2 = {
  displayName?: string;
  avatarImageUrl?: string | null;
  /** @deprecated Use avatarImageUrl. Kept until 2026-09-30 for mobile clients. */
  avatarUrl?: string | null;
};

type UpdateAccountCommand = {
  accountId: AccountId;
  displayName: string | null;
  avatarImageUrl: string | null;
};

type ContractCheck = {
  name: string;
  pass: boolean;
};

function normalizeOptionalText(value: string | null | undefined): string | null {
  if (value === undefined || value === null) {
    return null;
  }

  const trimmed = value.trim();
  return trimmed.length === 0 ? null : trimmed;
}

function toAccountDtoV2(account: Account): AccountDtoV2 {
  const avatarImageUrl = account.avatarImageUrl;

  return {
    id: account.id,
    displayName: account.displayName,
    avatarImageUrl,
    avatarUrl: avatarImageUrl,
    updatedAt: account.updatedAt.toISOString(),
  };
}

function fromUpdateAccountDtoV2(
  accountId: AccountId,
  dto: UpdateAccountDtoV2,
): UpdateAccountCommand {
  const avatarInput = dto.avatarImageUrl !== undefined ? dto.avatarImageUrl : dto.avatarUrl;

  return {
    accountId,
    displayName: normalizeOptionalText(dto.displayName),
    avatarImageUrl: normalizeOptionalText(avatarInput),
  };
}

function contractChecks(account: Account): ContractCheck[] {
  const dto = toAccountDtoV2(account);
  const commandFromNewField = fromUpdateAccountDtoV2(account.id, {
    avatarImageUrl: " https://example.com/new.png ",
  });
  const commandFromDeprecatedField = fromUpdateAccountDtoV2(account.id, {
    avatarUrl: " https://example.com/old.png ",
  });

  return [
    {
      name: "v2 response keeps deprecated avatarUrl during migration window",
      pass: dto.avatarUrl === dto.avatarImageUrl,
    },
    {
      name: "new input field wins when present",
      pass: commandFromNewField.avatarImageUrl === "https://example.com/new.png",
    },
    {
      name: "deprecated input field still maps to the domain command",
      pass: commandFromDeprecatedField.avatarImageUrl === "https://example.com/old.png",
    },
  ];
}

const account: Account = {
  id: "account_1" as AccountId,
  displayName: "Grace Hopper",
  avatarImageUrl: "https://example.com/grace.png",
  updatedAt: new Date("2026-06-09T00:00:00.000Z"),
};

const checks = contractChecks(account);

if (checks.some((check) => !check.pass)) {
  throw new Error("DTO migration contract check failed");
}

console.log(checks.map((check) => check.name).join("; "));
```

把代码块保存为 `deprecated-dto-fields-need-migration-window-tests.ts` 后，可用下面的命令做最小编译验证：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom deprecated-dto-fields-need-migration-window-tests.ts
```

注意 `Account` 领域模型里只有当前业务字段 `avatarImageUrl`，没有旧接口字段 `avatarUrl`。兼容窗口、弃用注释、回退读取和契约检查都被限制在 v2 DTO 边界。

**坑**：

- 不要只改 TypeScript 类型就删除字段；真实消费者可能不是同一个仓库里的 TypeScript 代码。
- 不要把旧字段回灌到领域模型；那会让接口历史变成业务事实。
- 不要让新旧字段互相覆盖得不透明；输入 mapper 要明确“新字段优先，旧字段回退”。
- 不要没有截止日期地永久保留弃用字段；迁移窗口应写进注释、文档和删除计划。

**检查**：

- DTO 中的弃用字段是否有 `@deprecated`、替代字段和计划删除时间。
- mapper 是否同时覆盖“新字段输入”和“旧字段输入”的契约测试。
- 领域模型是否没有出现旧字段名、别名或版本号。
- 删除弃用字段前，是否已有客户端迁移确认、监控观察和契约测试更新。
