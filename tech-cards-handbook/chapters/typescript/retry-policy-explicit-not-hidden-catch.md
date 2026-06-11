# 重试策略要显式化，而不是藏在 catch 分支里

**问题**：调用数据库、HTTP API、队列或文件系统失败时，什么时候该重试？如果把 `for` 循环直接写在 `catch` 分支里，后续很容易看不清哪些错误可重试、最多试几次、退避多久，以及耗尽后抛什么。

**要点**：

- 先把错误分成可重试、不可重试和调用方需要处理的领域错误；不要靠字符串匹配底层错误消息。
- 用 `RetryPolicy` 之类的小对象表达最大尝试次数和退避间隔，让策略能被测试、配置和复用。
- 重试函数只负责"按策略重新调用一次操作"；业务函数仍然负责把底层错误转换成领域错误。
- 重试耗尽后要保留原始错误链（`cause`）；日志或上层 handler 才能看到根因。

| 维度 | 隐式 catch 循环 | 显式策略 |
|---|---|---|
| 可重试条件 | 散落在 `catch (e)` 字符串判断里 | `isRetryable(e)` 单独定义 |
| 次数和退避 | 魔法数字写在循环体 | `{ maxAttempts, backoffMs }` |
| 测试方式 | 只能跑完整业务流程 | 可注入假操作和零退避 |
| 耗尽语义 | 经常只 `throw e` | 包装为 `RetryExhaustedError` 保留 `cause` |

**示例**：

```typescript
// npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom

class AppError extends Error {
  override readonly name: string;
  readonly cause?: unknown;
  constructor(message: string, cause?: unknown) {
    super(message);
    this.name = new.target.name;
    this.cause = cause;
  }
}

class TemporaryError extends AppError {}
class ForbiddenError extends AppError {}
class RetryExhaustedError extends AppError {}

interface RetryPolicy {
  maxAttempts: number;
  backoffMs: number;
}

function isRetryable(error: unknown): boolean {
  return error instanceof TemporaryError;
}

async function withRetry<T>(
  policy: RetryPolicy,
  call: () => Promise<T>,
): Promise<T> {
  const maxAttempts = Math.max(1, policy.maxAttempts);
  let lastError: unknown;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await call();
    } catch (error: unknown) {
      if (!isRetryable(error)) {
        throw error;
      }
      lastError = error;
      if (attempt < maxAttempts && policy.backoffMs > 0) {
        await new Promise((r) => setTimeout(r, policy.backoffMs));
      }
    }
  }

  throw new RetryExhaustedError(
    `retry exhausted after ${maxAttempts} attempts`,
    lastError,
  );
}

// --- verify ---

async function main(): Promise<void> {
  // success after retries
  let attempts = 0;
  const result = await withRetry({ maxAttempts: 3, backoffMs: 0 }, async () => {
    attempts++;
    if (attempts < 3) {
      throw new TemporaryError(`attempt ${attempts} failed`);
    }
    return "profile-ok";
  });
  if (result !== "profile-ok" || attempts !== 3) {
    throw new Error(`unexpected: result=${result} attempts=${attempts}`);
  }

  // non-retryable error passes through immediately
  let forbiddenCaught = false;
  try {
    await withRetry({ maxAttempts: 3, backoffMs: 0 }, async () => {
      throw new ForbiddenError("forbidden");
    });
  } catch (e: unknown) {
    forbiddenCaught = e instanceof ForbiddenError;
  }
  if (!forbiddenCaught) {
    throw new Error("expected ForbiddenError to pass through");
  }

  // retry exhausted preserves root cause
  let exhaustedCaught = false;
  try {
    await withRetry({ maxAttempts: 2, backoffMs: 0 }, async () => {
      throw new TemporaryError("always temporary");
    });
  } catch (e: unknown) {
    exhaustedCaught =
      e instanceof RetryExhaustedError &&
      e.cause instanceof TemporaryError;
  }
  if (!exhaustedCaught) {
    throw new Error("expected RetryExhaustedError with TemporaryError cause");
  }

  const ok: string = result;
  console.log(`pass: ${ok}`);
}

main().catch((e: unknown) => {
  console.error(e);
  throw e;
});
```

**坑**：

- 把重试次数、退避和错误判断直接塞进 service 方法，导致每个调用点都有一份不同的重试规则。
- 用 `(error as Error).message.includes("timeout")` 判断是否重试；底层 SDK 改了错误文案，恢复策略就失效。
- 重试耗尽后返回一个全新的错误字符串，忘记传 `cause`，调用方无法通过 `instanceof` 判断根因。
- 对不可重试错误也继续重试，放大权限错误、参数错误或幂等性问题。

**检查**：

- 可重试错误集合是否有稳定的自定义错误类型，而不是散落的字符串判断？
- 最大尝试次数、退避间隔和是否开启重试是否能在测试里设成小值或零值？
- 重试耗尽后，`cause` 还能否通过 `instanceof` 命中最后一次失败的根因？
- handler 或 CLI 对外输出是否只暴露安全错误码，而不是直接拼接底层 SDK / 数据库错误？

**对照阅读**：

- Go: [`go/retry-policy-explicit-not-hidden-loop.md`](go/retry-policy-explicit-not-hidden-loop.md)
- Rust: [`rust/retry-strategy-explicit-not-implicit-loop.md`](rust/retry-strategy-explicit-not-implicit-loop.md)
- Python: [`python/retry-policy-explicit-not-hidden-loop.md`](python/retry-policy-explicit-not-hidden-loop.md)
