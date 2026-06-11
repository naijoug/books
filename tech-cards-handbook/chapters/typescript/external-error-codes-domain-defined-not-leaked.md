# 对外错误码应由领域错误翻译，而不是泄漏底层异常

## 什么时候用

当 TypeScript 服务需要把 repository、第三方 SDK、文件系统或队列客户端的异常转换成 HTTP response、RPC error、webhook 回调或前端可展示错误时。对外契约不应该暴露 `SQLSTATE`、索引名、主机地址、SDK 类名或 stack trace；这些信息应该留在日志和 tracing 里。对外只输出稳定的领域错误码，例如 `USER_NOT_FOUND`、`EMAIL_ALREADY_USED`、`SERVICE_OVERLOADED`。

## 怎么写

```ts
// external-error-codes-domain-defined-not-leaked.ts
type ErrorCode =
  | "USER_NOT_FOUND"
  | "EMAIL_ALREADY_USED"
  | "SERVICE_OVERLOADED"
  | "INTERNAL_ERROR";

class AppError extends Error {
  readonly name = "AppError";

  constructor(
    readonly code: ErrorCode,
    message: string,
    readonly inner?: unknown,
  ) {
    super(message);
  }
}

class UserNotFoundError extends AppError {
  constructor(readonly userId: string, inner?: unknown) {
    super("USER_NOT_FOUND", "user not found", inner);
  }
}

class EmailAlreadyUsedError extends AppError {
  constructor(inner?: unknown) {
    super("EMAIL_ALREADY_USED", "email already used", inner);
  }
}

class ServiceOverloadedError extends AppError {
  constructor(inner?: unknown) {
    super("SERVICE_OVERLOADED", "service overloaded", inner);
  }
}

type StorageError =
  | { kind: "row-not-found"; detail: string }
  | { kind: "unique-violation"; detail: string }
  | { kind: "pool-exhausted"; detail: string }
  | { kind: "driver-error"; detail: string };

function translateStorageError(error: StorageError, userId: string): AppError {
  switch (error.kind) {
    case "row-not-found":
      return new UserNotFoundError(userId, error);
    case "unique-violation":
      return new EmailAlreadyUsedError(error);
    case "pool-exhausted":
      return new ServiceOverloadedError(error);
    case "driver-error":
      return new AppError("INTERNAL_ERROR", "internal server error", error);
  }
}

function loadUserName(userId: string): string {
  const rawErrorByUser: Record<string, StorageError | undefined> = {
    missing: { kind: "row-not-found", detail: "sql: no rows in result set" },
    duplicate: {
      kind: "unique-violation",
      detail: "SQLSTATE 23505 duplicate key users_email_key",
    },
    overloaded: { kind: "pool-exhausted", detail: "db pool exhausted at 10.0.0.12" },
    broken: { kind: "driver-error", detail: "trace /srv/app/repository.ts:17" },
  };

  const storageError = rawErrorByUser[userId];
  if (storageError) {
    throw translateStorageError(storageError, userId);
  }
  return "Alice";
}

type PublicErrorResponse = {
  status: 404 | 409 | 500 | 503;
  body: { code: ErrorCode; message: string };
};

function toPublicResponse(error: unknown): PublicErrorResponse {
  const appError =
    error instanceof AppError
      ? error
      : new AppError("INTERNAL_ERROR", "internal server error", error);

  const statusByCode: Record<ErrorCode, PublicErrorResponse["status"]> = {
    USER_NOT_FOUND: 404,
    EMAIL_ALREADY_USED: 409,
    SERVICE_OVERLOADED: 503,
    INTERNAL_ERROR: 500,
  };

  return {
    status: statusByCode[appError.code],
    body: { code: appError.code, message: appError.message },
  };
}

function verify(): void {
  if (loadUserName("ok") !== "Alice") {
    throw new Error("normal path broken");
  }

  const cases: Array<[string, PublicErrorResponse["status"], ErrorCode]> = [
    ["missing", 404, "USER_NOT_FOUND"],
    ["duplicate", 409, "EMAIL_ALREADY_USED"],
    ["overloaded", 503, "SERVICE_OVERLOADED"],
    ["broken", 500, "INTERNAL_ERROR"],
  ];

  for (const [userId, expectedStatus, expectedCode] of cases) {
    try {
      loadUserName(userId);
      throw new Error(`${userId} should fail`);
    } catch (error: unknown) {
      const response = toPublicResponse(error);
      const publicText = JSON.stringify(response.body);

      if (response.status !== expectedStatus || response.body.code !== expectedCode) {
        throw new Error(`unexpected public response for ${userId}`);
      }
      if (
        publicText.includes("SQLSTATE") ||
        publicText.includes("users_email_key") ||
        publicText.includes("10.0.0.12") ||
        publicText.includes("/srv/app")
      ) {
        throw new Error("infrastructure detail leaked to public response");
      }
      if (error instanceof AppError && error.inner === undefined) {
        throw new Error("inner cause chain lost");
      }
    }
  }
}

verify();
```

## 哪里容易错

1. **把底层错误类型直接当 code**：`QueryFailedError`、`PrismaClientKnownRequestError`、`FetchError` 是实现细节，不是产品契约。
2. **把 `String(error)` 塞进响应**：底层错误字符串经常带 SQL state、索引名、host、路径或 SDK 内部字段。
3. **翻译时丢掉根因**：对外不能泄漏细节，但内部仍应通过 `inner` / `cause` / structured log 保留排障线索。
4. **在 handler 里到处写字符串判断**：`if (message.includes("duplicate key"))` 会让对外契约依赖底层文案；应在 adapter 边界统一翻译成领域错误。

## 一句话总结

TypeScript 的 handler 不应该认识数据库或 SDK 的错误文案；adapter 把底层异常翻译成领域错误，边界层只输出稳定 `code` 和安全 `message`，同时保留内部根因供日志与追踪使用。
