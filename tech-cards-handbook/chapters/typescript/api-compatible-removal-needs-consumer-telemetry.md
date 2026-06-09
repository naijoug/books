# API 兼容删除需要消费者观测信号

**问题**：

字段、事件版本或 endpoint 已经标记弃用后，团队很容易在迁移窗口结束当天直接删除。问题是“没人反馈还在用”不等于“没人还在用”：老移动端、定时脚本、第三方集成和低频客户可能不会出现在本仓库的编译结果里。没有消费者观测信号的兼容删除，本质上是在盲删外部契约。

**要点**：

- 删除外部契约前，要先能观察谁还在使用旧契约。
- 观测信号应绑定到 API 版本、字段名、客户端标识和迁移截止时间。
- 旧字段读取、旧版本响应和旧事件发布都要打点；只看服务端类型覆盖率不够。
- 删除判断应由 telemetry summary / dashboard / 契约测试共同支撑，而不是靠口头确认。
- 删除代码时也删除对应的旧指标、兼容 mapper 和契约测试，避免留下僵尸兼容层。

**示例**：

```typescript
type Brand<T, Name extends string> = T & { readonly __brand: Name };

type AccountId = Brand<string, "AccountId">;

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

type ApiClient = {
  id: string;
  version: string;
};

type DeprecationMetric = {
  contract: "UpdateAccountDtoV2.avatarUrl";
  clientId: string;
  clientVersion: string;
  observedAt: string;
  removalAfter: string;
};

type Telemetry = {
  trackDeprecatedContractUse(metric: DeprecationMetric): void;
};

class InMemoryTelemetry implements Telemetry {
  readonly metrics: DeprecationMetric[] = [];

  trackDeprecatedContractUse(metric: DeprecationMetric): void {
    this.metrics.push(metric);
  }
}

function normalizeOptionalText(value: string | null | undefined): string | null {
  if (value === undefined || value === null) {
    return null;
  }

  const trimmed = value.trim();
  return trimmed.length === 0 ? null : trimmed;
}

function fromUpdateAccountDtoV2(
  accountId: AccountId,
  dto: UpdateAccountDtoV2,
  client: ApiClient,
  telemetry: Telemetry,
  now: Date,
): UpdateAccountCommand {
  if (dto.avatarImageUrl === undefined && dto.avatarUrl !== undefined) {
    telemetry.trackDeprecatedContractUse({
      contract: "UpdateAccountDtoV2.avatarUrl",
      clientId: client.id,
      clientVersion: client.version,
      observedAt: now.toISOString(),
      removalAfter: "2026-09-30",
    });
  }

  const avatarInput = dto.avatarImageUrl !== undefined ? dto.avatarImageUrl : dto.avatarUrl;

  return {
    accountId,
    displayName: normalizeOptionalText(dto.displayName),
    avatarImageUrl: normalizeOptionalText(avatarInput),
  };
}

function canRemoveDeprecatedContract(
  metrics: DeprecationMetric[],
  today: Date,
  quietDays: number,
): boolean {
  const lastUse = metrics
    .filter((metric) => metric.contract === "UpdateAccountDtoV2.avatarUrl")
    .map((metric) => new Date(metric.observedAt).getTime())
    .sort((left, right) => right - left)[0];

  if (lastUse === undefined) {
    return true;
  }

  const quietWindowMs = quietDays * 24 * 60 * 60 * 1000;
  return today.getTime() - lastUse >= quietWindowMs;
}

const telemetry = new InMemoryTelemetry();
const accountId = "account_1" as AccountId;
const client: ApiClient = { id: "ios-app", version: "4.8.0" };

const command = fromUpdateAccountDtoV2(
  accountId,
  { avatarUrl: " https://example.com/old.png " },
  client,
  telemetry,
  new Date("2026-09-20T00:00:00.000Z"),
);

const isSafeToRemove = canRemoveDeprecatedContract(
  telemetry.metrics,
  new Date("2026-10-01T00:00:00.000Z"),
  14,
);

if (command.avatarImageUrl !== "https://example.com/old.png") {
  throw new Error("deprecated input field was not mapped");
}

if (telemetry.metrics.length !== 1 || isSafeToRemove) {
  throw new Error("deprecated contract removal is not backed by telemetry");
}

console.log(telemetry.metrics[0].contract);
```

把代码块保存为 `api-compatible-removal-needs-consumer-telemetry.ts` 后，可用下面的命令做最小编译验证：

```bash
npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom api-compatible-removal-needs-consumer-telemetry.ts
```

这个例子没有把 `avatarUrl` 回灌到领域模型，而是在兼容 adapter 里同时完成旧字段回退和弃用使用打点。删除旧字段前，团队至少能看到最近是否仍有客户端发送旧字段。

**坑**：

- 不要把“没有工单反馈”当成“没有消费者使用”。
- 不要只对响应输出打点；输入字段、Webhook payload、消息 topic 和旧 endpoint 都可能被消费者依赖。
- 不要把 telemetry 写进领域模型；观测逻辑属于 adapter / gateway / publisher 边界。
- 不要在删除旧契约后继续保留旧指标名；否则 dashboard 会变成误导性的僵尸信号。

**检查**：

- 弃用契约是否有 client id、版本、字段或 topic 名称、观察时间和计划删除时间。
- 删除前是否能证明最近一段 quiet window 内没有真实消费者命中旧契约。
- 契约测试是否覆盖“旧字段仍可读取并打点”和“迁移完成后删除兼容分支”。
- 删除 PR 是否同时移除旧 mapper 分支、旧测试、旧指标和文档中的迁移说明。
