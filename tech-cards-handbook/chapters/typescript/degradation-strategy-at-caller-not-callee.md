# 降级策略应在调用方决定，而不是被调方隐藏

## 什么时候用

当 TypeScript service 依赖缓存、画像服务、推荐服务、第三方 API 或搜索服务时。被调方只应该返回真实结果或抛出可分类错误；是否用默认值、缓存、简化响应继续服务，必须由调用方按业务场景决定。

典型判断：同一个 `ProfileClient` 超时，在推荐页可以降级成"匿名用户"，在支付风控里必须中断。把降级藏在 client 里，会让上层永远分不清"真的没有数据"和"依赖失败后被伪装成空数据"。

## 怎么写

```typescript
// degradation-strategy-at-caller-not-callee.ts

class ProfileError extends Error {
  constructor(message: string, public readonly inner?: Error) {
    super(message);
    this.name = "ProfileError";
  }
}

class ProfileNotFoundError extends ProfileError {
  constructor(message: string) {
    super(message);
    this.name = "ProfileNotFoundError";
  }
}

class ProfileServiceUnavailableError extends ProfileError {
  constructor(message: string, inner?: Error) {
    super(message, inner);
    this.name = "ProfileServiceUnavailableError";
  }
}

interface Profile {
  userId: string;
  displayName: string;
  verified: boolean;
}

interface DisplayNameResult {
  value: string;
  degraded: boolean;
}

class ProfileClient {
  fetch(userId: string): Profile {
    // 被调方只报告事实：成功返回 Profile，失败抛出可分类错误。
    // 不要在这里返回 { userId, displayName: "anonymous", verified: false } 伪装成功。
    if (userId === "missing") {
      throw new ProfileNotFoundError("profile not found");
    }
    if (userId === "timeout") {
      throw new ProfileServiceUnavailableError("profile service timeout");
    }
    return { userId, displayName: "Ada", verified: true };
  }
}

class RecommendationService {
  constructor(private client: ProfileClient) {}

  displayNameForCard(userId: string): DisplayNameResult {
    try {
      const profile = this.client.fetch(userId);
      return { value: profile.displayName, degraded: false };
    } catch (e: unknown) {
      if (e instanceof ProfileNotFoundError) {
        // 推荐卡片允许"用户缺少画像"降级，但必须标记 degraded。
        return { value: "anonymous", degraded: true };
      }
      if (e instanceof ProfileServiceUnavailableError) {
        // 依赖故障不是"没有画像"，继续传播给上层重试/熔断/告警。
        throw new ProfileServiceUnavailableError(
          `cannot render recommendation card for ${userId}`,
          e
        );
      }
      throw e;
    }
  }
}

class PaymentRiskService {
  constructor(private client: ProfileClient) {}

  verifiedProfile(userId: string): Profile {
    try {
      return this.client.fetch(userId);
    } catch (e: unknown) {
      if (e instanceof ProfileError) {
        // 支付风控不能用默认画像继续走；这里必须保留 inner 并中断。
        throw new ProfileError(
          `cannot verify payer profile for ${userId}`,
          e
        );
      }
      throw e;
    }
  }
}

// --- verify ---

function verify(): void {
  const client = new ProfileClient();
  const recommendation = new RecommendationService(client);
  const payment = new PaymentRiskService(client);

  const ok = recommendation.displayNameForCard("u-1");
  if (ok.value !== "Ada" || ok.degraded !== false) {
    throw new Error(`expected non-degraded Ada, got ${JSON.stringify(ok)}`);
  }

  const fallback = recommendation.displayNameForCard("missing");
  if (fallback.value !== "anonymous" || fallback.degraded !== true) {
    throw new Error(`expected degraded anonymous, got ${JSON.stringify(fallback)}`);
  }

  try {
    recommendation.displayNameForCard("timeout");
    throw new Error("service outage must not be silently degraded");
  } catch (e: unknown) {
    if (!(e instanceof ProfileServiceUnavailableError)) throw e;
    if (!(e.inner instanceof ProfileServiceUnavailableError)) {
      throw new Error("inner cause chain lost");
    }
    if (!e.message.includes("recommendation card")) {
      throw new Error(`unexpected message: ${e.message}`);
    }
  }

  try {
    payment.verifiedProfile("missing");
    throw new Error("payment risk must not use fake profile");
  } catch (e: unknown) {
    if (!(e instanceof ProfileError)) throw e;
    if (!(e.inner instanceof ProfileNotFoundError)) {
      throw new Error("inner cause chain lost");
    }
    if (!e.message.includes("verify payer profile")) {
      throw new Error(`unexpected message: ${e.message}`);
    }
  }
}

verify();
```

## 要点

- 被调方（client / repository / SDK adapter）只负责把底层失败翻译成可分类错误，不负责替上层选择默认值。
- 调用方按业务语义显式决定：哪些错误可以降级，哪些错误必须传播。
- 降级结果要可观测，例如返回 `degraded: true`、打 metric、写日志或 trace tag。
- 不可降级路径仍要用 `inner` / `cause` 保留错误链，方便上层 handler / CLI 继续分类。

## 容易踩坑

- **在 client 里返回空对象**：`return { userId, displayName: "", verified: false }` 会把 404、timeout、decode error 混成同一种"空画像"。
- **裸 `catch` 后统一降级**：推荐页可以降级，不代表支付、风控、发货也可以降级。
- **降级但不标记**：调用方和观测系统看不到默认值来源，事故时无法判断影响面。
- **把错误链截断**：重新抛出 `new ProfileError("failed")` 但不传 `inner`，上层无法知道根因是 not found 还是 timeout。

## 检查

- 搜索 client / repository 是否在 catch 分支返回默认对象、空数组或空字符串。
- 对每个调用方列出"可降级错误"和"必须传播错误"，不要只写一个 `catch (e)`。
- 验证降级响应包含可观测标记；不可降级响应保留 `inner` / `cause`。
- 编译检查：`npx tsc --noEmit --strict degradation-strategy-at-caller-not-callee.ts`。

## 延伸阅读

- Go 对照：[`../go/degradation-strategy-at-caller-not-callee.md`](../go/degradation-strategy-at-caller-not-callee.md)
- Rust 对照：[`../rust/degradation-strategy-at-caller-not-callee.md`](../rust/degradation-strategy-at-caller-not-callee.md)
- Python 对照：[`../python/degradation-strategy-at-caller-not-callee.md`](../python/degradation-strategy-at-caller-not-callee.md)
