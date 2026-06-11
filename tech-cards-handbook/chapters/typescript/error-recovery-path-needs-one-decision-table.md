# 错误恢复路径需要一张决策表串起来

**问题**：TypeScript 项目里常见的错误处理会分散在 `throw`、`catch`、`Result`、React query retry、API handler 和 mapper 中。每一段看起来都合理，但 review 时很难确认“这个错误到底该重试、降级、返回用户可见错误，还是升级为内部故障”。错误恢复路径需要一张决策表，把领域错误码、调用方动作、重试/降级标记和对外响应串成同一条可审查链路。

**要点**：

- 先定义稳定的领域 `ErrorCode`，再让 adapter 把底层错误翻译成 `AppError`。
- 决策表同时写 `action`、`retryable`、`degraded`、`publicCode` 和 `publicMessage`，不要只写 HTTP status。
- 调用方可以把某个默认“返回公开错误”改成局部降级，但必须返回可观测的 `degraded` 标记。
- 对外响应只读取决策表里的安全字段；底层 SQL state、host、trace、文件路径保留在 `inner` 里用于日志。

| 维度 | 零散 `catch` | 决策表 |
|---|---|---|
| 错误分类 | 多处 `instanceof` / 字符串判断 | 领域 `ErrorCode` 统一登记 |
| 恢复动作 | 重试、降级、对外 code 分散实现 | `RecoveryAction` 明确表达 |
| 对外契约 | handler 拼接 `error.message` | `publicCode` / `publicMessage` 稳定输出 |
| 审查方式 | 需要读完整调用链 | 一张表能发现缺口 |

**示例**：

```ts
type ErrorCode =
  | "PROFILE_NOT_FOUND"
  | "PROFILE_TEMPORARILY_UNAVAILABLE"
  | "INTERNAL_ERROR";

type RecoveryAction = "retry" | "degrade" | "return_public_error" | "escalate";

type RecoveryDecision = Readonly<{
  action: RecoveryAction;
  publicCode: ErrorCode;
  publicMessage: string;
  retryable: boolean;
  degraded: boolean;
}>;

class AppError extends Error {
  readonly code: ErrorCode;
  readonly inner?: unknown;

  constructor(code: ErrorCode, message: string, inner?: unknown) {
    super(message);
    this.name = "AppError";
    this.code = code;
    this.inner = inner;
  }
}

const decisionTable = {
  PROFILE_NOT_FOUND: {
    action: "return_public_error",
    publicCode: "PROFILE_NOT_FOUND",
    publicMessage: "profile not found",
    retryable: false,
    degraded: false,
  },
  PROFILE_TEMPORARILY_UNAVAILABLE: {
    action: "retry",
    publicCode: "PROFILE_TEMPORARILY_UNAVAILABLE",
    publicMessage: "profile service is temporarily unavailable",
    retryable: true,
    degraded: false,
  },
  INTERNAL_ERROR: {
    action: "escalate",
    publicCode: "INTERNAL_ERROR",
    publicMessage: "internal server error",
    retryable: false,
    degraded: false,
  },
} satisfies Record<ErrorCode, RecoveryDecision>;

function decideRecovery(error: AppError): RecoveryDecision {
  return decisionTable[error.code];
}

function displayNameOrDegrade(error: AppError): { name: string; decision: RecoveryDecision } {
  if (error.code !== "PROFILE_NOT_FOUND") {
    throw error;
  }

  const base = decideRecovery(error);
  return {
    name: "anonymous",
    decision: {
      ...base,
      action: "degrade",
      retryable: false,
      degraded: true,
    },
  };
}

function toPublicResponse(error: AppError): { code: ErrorCode; message: string } {
  const decision = decideRecovery(error);
  return {
    code: decision.publicCode,
    message: decision.publicMessage,
  };
}

type StorageError =
  | { kind: "not_found"; detail: string }
  | { kind: "timeout"; host: string; traceId: string }
  | { kind: "corrupted"; path: string };

function translateStorageError(error: StorageError): AppError {
  switch (error.kind) {
    case "not_found":
      return new AppError("PROFILE_NOT_FOUND", "profile not found", error);
    case "timeout":
      return new AppError(
        "PROFILE_TEMPORARILY_UNAVAILABLE",
        "profile temporarily unavailable",
        error,
      );
    case "corrupted":
      return new AppError("INTERNAL_ERROR", "internal server error", error);
  }
}

const missing = translateStorageError({
  kind: "not_found",
  detail: "sql: no rows in result set for profile_id=42",
});
const degraded = displayNameOrDegrade(missing);
console.assert(degraded.name === "anonymous", "missing profile should use fallback name");
console.assert(degraded.decision.action === "degrade", "caller should record degrade action");
console.assert(degraded.decision.degraded, "degrade should be observable");

const temporary = translateStorageError({
  kind: "timeout",
  host: "10.0.0.8",
  traceId: "trace=abc",
});
const retryDecision = decideRecovery(temporary);
console.assert(retryDecision.action === "retry", "temporary profile error should retry");
console.assert(retryDecision.retryable, "retryable flag should be explicit");

const response = JSON.stringify(toPublicResponse(temporary));
console.assert(response.includes("PROFILE_TEMPORARILY_UNAVAILABLE"), "public code should be stable");
console.assert(!response.includes("10.0.0.8"), "public response leaked host");
console.assert(!response.includes("trace=abc"), "public response leaked trace");
console.assert(JSON.stringify(temporary.inner).includes("10.0.0.8"), "inner cause should keep diagnostics");

const corrupted = translateStorageError({
  kind: "corrupted",
  path: "/var/lib/profiles/42.json",
});
console.assert(decideRecovery(corrupted).action === "escalate", "corrupted data should escalate");
console.assert(!JSON.stringify(toPublicResponse(corrupted)).includes("/var/lib"), "public response leaked path");
```

**坑**：

- 只新增一个 `ErrorCode`，不更新 `decisionTable`。使用 `satisfies Record<ErrorCode, RecoveryDecision>` 可以让编译器提示缺口。
- handler 里直接返回 `error.message`，把 adapter 的 SQL、host、trace 或路径暴露给外部消费者。
- 把重试写在请求库配置里、降级写在 UI 组件里、对外 code 写在 API handler 里，导致同一错误在不同入口表现不一致。
- 被调方静默返回默认对象，让调用方无法区分“数据不存在”“依赖临时故障”和“内部数据损坏”。

**检查**：

- 每个 `ErrorCode` 是否都能在一张表里看到默认动作、是否可重试、是否可降级和对外错误码？
- 调用方做局部降级时，是否返回或记录 `degraded: true`，而不是悄悄给默认值？
- 对外响应是否只读取 `publicCode` / `publicMessage`，不直接输出 `inner` 或 `error.message`？
- 新增领域错误码时，`satisfies Record<ErrorCode, RecoveryDecision>` 和最小测试是否能失败提示“决策表未覆盖”？

**延伸阅读**：

- TypeScript 错误分类：[`custom-error-types-make-failures-classifiable.md`](custom-error-types-make-failures-classifiable.md)
- TypeScript 显式重试：[`retry-policy-explicit-not-hidden-catch.md`](retry-policy-explicit-not-hidden-catch.md)
- TypeScript 调用方降级：[`degradation-strategy-at-caller-not-callee.md`](degradation-strategy-at-caller-not-callee.md)
- TypeScript 对外错误码：[`external-error-codes-domain-defined-not-leaked.md`](external-error-codes-domain-defined-not-leaked.md)
- Python 决策表对照：[`../python/error-recovery-path-needs-one-decision-table.md`](../python/error-recovery-path-needs-one-decision-table.md)
- Go 决策表对照：[`../go/error-recovery-path-needs-one-decision-table.md`](../go/error-recovery-path-needs-one-decision-table.md)
- Rust 决策表对照：[`../rust/error-recovery-path-needs-one-decision-table.md`](../rust/error-recovery-path-needs-one-decision-table.md)
