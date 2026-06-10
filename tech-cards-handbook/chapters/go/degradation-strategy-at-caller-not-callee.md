# 降级策略要在调用方实现，而不是在被调方隐藏

**问题**：外部服务、缓存、推荐模型或配置中心不可用时，代码很容易在 client / repository 层直接返回默认值并吞掉错误。这样短期看起来“系统没报错”，长期会让调用方无法区分真实成功、降级成功和不可接受的业务失败。

**要点**：

- 被调方只报告真实结果：`(Profile, error)`、`(Config, error)`，不要静默返回默认对象和 `nil`。
- 调用方根据业务语义决定是否降级：推荐流可以返回匿名画像，支付、权限、库存扣减通常不能降级。
- 降级也要可观测：至少记录日志、metric 或在响应内部状态里标记 `degraded=true`，不要把它伪装成普通成功。
- 降级策略和重试策略分开：先用显式重试处理暂时性错误；重试耗尽后，再由调用方决定是否降级。

| 维度 | 被调方静默降级 | 调用方显式降级 |
|---|---|---|
| 业务语义 | 被调方猜测所有场景都能接受默认值 | 每个调用方按自己的容忍度决策 |
| 可观测性 | 错误被吞掉，监控看起来全绿 | 降级分支可打日志、metric、trace |
| 测试方式 | 很难覆盖“真实成功 vs 假成功” | 可以分别测试可降级和不可降级调用方 |
| 失败传播 | 调用方无法拒绝危险降级 | 不可降级场景继续返回错误 |

**示例**：

```go
package main

import (
	"errors"
	"fmt"
)

var (
	ErrProfileTimeout     = errors.New("profile service timeout")
	ErrProfileUnavailable = errors.New("profile service unavailable")
	ErrProfileNotFound    = errors.New("profile not found")
)

type Profile struct {
	Name  string
	Email string
}

// 被调方：只报告真实结果，不做降级。
func fetchProfile(userID string) (Profile, error) {
	switch userID {
	case "timeout":
		return Profile{}, fmt.Errorf("fetch profile %s: %w", userID, ErrProfileTimeout)
	case "down":
		return Profile{}, fmt.Errorf("fetch profile %s: %w", userID, ErrProfileUnavailable)
	case "missing":
		return Profile{}, fmt.Errorf("fetch profile %s: %w", userID, ErrProfileNotFound)
	default:
		return Profile{Name: "User-" + userID, Email: userID + "@example.com"}, nil
	}
}

type RecommendationService struct{}

func (RecommendationService) DisplayName(userID string) (string, bool, error) {
	profile, err := fetchProfile(userID)
	if err == nil {
		return profile.Name, false, nil
	}
	if errors.Is(err, ErrProfileNotFound) || errors.Is(err, ErrProfileTimeout) || errors.Is(err, ErrProfileUnavailable) {
		// 推荐场景能接受匿名画像，但要显式标记 degraded。
		fmt.Printf("WARN profile unavailable for recommendation: %v\n", err)
		return "anonymous", true, nil
	}
	return "", false, err
}

type PaymentService struct{}

func (PaymentService) VerifiedProfile(userID string) (Profile, error) {
	profile, err := fetchProfile(userID)
	if err != nil {
		// 支付场景不能把匿名画像当作真实用户，必须传播失败。
		return Profile{}, fmt.Errorf("cannot start payment for %s: %w", userID, err)
	}
	return profile, nil
}

func main() {
	rec := RecommendationService{}
	pay := PaymentService{}

	name, degraded, err := rec.DisplayName("timeout")
	if err != nil || name != "anonymous" || !degraded {
		panic(fmt.Sprintf("expected recommendation degradation, name=%q degraded=%v err=%v", name, degraded, err))
	}
	fmt.Println("recommendation degraded explicitly")

	_, err = pay.VerifiedProfile("timeout")
	if !errors.Is(err, ErrProfileTimeout) {
		panic(fmt.Sprintf("expected payment to keep timeout root cause, got %v", err))
	}
	fmt.Println("payment rejected degradation and kept root cause")

	name, degraded, err = rec.DisplayName("123")
	if err != nil || degraded || name != "User-123" {
		panic(fmt.Sprintf("expected real profile, name=%q degraded=%v err=%v", name, degraded, err))
	}
	fmt.Println("normal path is not marked degraded")
}
```

**坑**：

- 在 `fetchProfile` / `LoadConfig` / `Repository.Get` 里 `return defaultValue, nil`，导致上层永远不知道依赖失败。
- 只有日志没有返回状态：调用方拿到默认值后仍然把它写入账单、权限或审计记录。
- 把降级和重试揉在同一个 `for` / `if err != nil` 分支里，最后既看不出什么时候重试，也看不出什么时候接受默认值。
- 降级后的响应对外看起来和真实成功完全一样，排障时无法区分业务质量下降和正常请求。

**检查**：

- 每个 client / repository 是否只返回真实结果和错误，而不是替调用方决定默认值？
- 每个调用方是否明确写出“哪些错误可降级、哪些错误必须传播”？
- 降级分支是否能被测试断言，例如 `degraded=true`、metric 增加或日志包含上下文？
- 不可降级路径是否仍保留 `%w` 错误链，让 handler / CLI 能稳定分类根因？

**Rust 对照**：Rust 版同一原则见 [`../rust/degradation-strategy-at-caller-not-callee.md`](../rust/degradation-strategy-at-caller-not-callee.md)。Rust 用 `Result<T, E>` 和 `match` 暴露降级分支；Go 用 `(T, error)`、`errors.Is` / `errors.As` 和显式返回值标记降级状态。两者共同点都是：被调方不伪装成功，调用方才拥有业务语义。
