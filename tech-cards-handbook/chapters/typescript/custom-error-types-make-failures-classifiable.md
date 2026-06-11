# 自定义错误类型让失败可分类

## 一句话

不要到处 `throw new Error("...")` 和 `catch (e) { console.error(e) }`；用领域错误类型表达"失败是什么"，让调用方按类型分支处理，而不是靠字符串匹配或 `any` 类型猜测。

## 什么时候用

- 函数需要抛出不同种类的失败，调用方要区分"重试"、"降级"、"用户输入错"和"系统故障"。
- `catch` 块只写 `console.error(e)` 或弹通用 toast，错误类型信息被吞掉。
- 多个模块各自 `throw`，上层需要统一捕获某一类而不是逐个列举。
- 与 `Result<T, E>` 搭配：可恢复错误用 `Result`，不可恢复 / 程序员错误用自定义 Error 子类。

## 怎么写

```ts
// === 定义 ===

class AppError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly cause?: unknown,
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

class NotFoundError extends AppError {
  constructor(
    public readonly resource: string,
    public readonly id: string,
    cause?: unknown,
  ) {
    super(`${resource.toUpperCase()}_NOT_FOUND`, `${resource} '${id}' 不存在`, cause);
  }
}

class RateLimitError extends AppError {
  constructor(
    public readonly service: string,
    public readonly retryAfterMs: number,
    cause?: unknown,
  ) {
    super("RATE_LIMITED", `${service} 限流，${retryAfterMs}ms 后可重试`, cause);
  }
}

// === 使用 ===

class UpstreamError extends Error {
  constructor(
    public readonly status: number,
    public readonly headers?: Record<string, string>,
  ) {
    super(`upstream ${status}`);
  }
}

function fetchProfile(id: string): { displayName: string } {
  if (id.startsWith("rate-")) {
    throw new UpstreamError(429, { "retry-after": "30" });
  }
  if (!id.startsWith("user-")) {
    throw new NotFoundError("profile", id);
  }
  return { displayName: `user-${id}` };
}

// === 调用方按类型分支 ===

function getDisplayName(id: string): { name: string; degraded: boolean } {
  try {
    const profile = fetchProfile(id);
    return { name: profile.displayName, degraded: false };
  } catch (e) {
    // 调用方按错误类型决定处理策略，而不是靠 message 字符串
    if (e instanceof NotFoundError) {
      return { name: `${e.resource}-${e.id} (degraded)`, degraded: true };
    }
    if (e instanceof RateLimitError) {
      // 限流可重试；这里降级处理
      return { name: `${e.service}-throttled (degraded)`, degraded: true };
    }
    // 不认识的错误继续抛出，不吞掉
    throw e;
  }
}

// === 验证 ===

function _verify() {
  // NotFound → 调用方降级
  const r1 = getDisplayName("missing-1");
  console.assert(
    r1.name === "profile-missing-1 (degraded)" && r1.degraded === true,
    `expected degraded for NotFound, got ${JSON.stringify(r1)}`,
  );

  // RateLimit → 调用方降级
  const r2 = getDisplayName("rate-1");
  console.assert(
    r2.name === "UpstreamError-throttled (degraded)" && r2.degraded === true,
    `expected degraded for RateLimit, got ${JSON.stringify(r2)}`,
  );

  // 正常路径
  const r3 = getDisplayName("user-42");
  console.assert(
    r3.name === "user-user-42" && r3.degraded === false,
    `expected normal, got ${JSON.stringify(r3)}`,
  );

  // 不认识的错误不吞掉
  let caught = false;
  try {
    // @ts-expect-error - 故意传 null 触发非预期路径
    fetchProfile(null);
  } catch {
    caught = true;
  }
  console.assert(caught, "unknown errors should propagate");
}

_verify();
```

## 注意事项

- `AppError` 基类保留 `code`（稳定错误码）、`message`（可读消息）和 `cause`（原始异常链）。调用方用 `instanceof` 按子类分支，不需要解析 `message` 字符串。
- `catch (e)` 里一定要判断类型后再处理；不认识的错误 `throw e` 继续传播，不要 `console.error` 吞掉。
- TypeScript 的 `catch (e)` 推断为 `unknown`，必须先缩窄再访问属性：`instanceof` 是最直接的缩窄方式。
- 对于可恢复、可预期的错误，也可以用 `Result<T, E>` 替代 `throw`（见 [`result-type-makes-errors-explicit.md`](result-type-makes-errors-explicit.md)）；两者可以并存：`Result` 给预期内业务分支，`throw` 给不可恢复故障。
- 不要在 `catch` 里用 `(e as any).message` 或 `(e as Error).status` 做隐式类型断言；如果需要访问自定义字段，先用 `instanceof` 缩窄到对应子类。

## 跨语言对照

- Python：[`custom-exception-hierarchy-makes-errors-classifiable.md`](../python/custom-exception-hierarchy-makes-errors-classifiable.md)
- Go：[`error-wrapping-vs-result-propagation.md`](../go/error-wrapping-vs-result-propagation.md)
- Rust：[`result-means-failable-with-reason.md`](../rust/result-means-failable-with-reason.md)
