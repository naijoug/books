# 错误恢复路径需要一张决策表串起来

## 什么时候用

当一个 service 同时涉及错误分类、重试、降级和对外错误码时。Go 代码很容易把这些决策分散在 `if err != nil`、`errors.Is`、handler `switch` 和 fallback 默认值里；每一处单看都合理，但 review 时看不出某个领域错误到底应该重试、降级、返回用户可见错误，还是升级为内部故障。

## 怎么写

```go
// error-recovery-path-needs-one-decision-table.go
package main

import (
	"errors"
	"fmt"
	"strings"
)

type ErrorCode string

const (
	CodeProfileNotFound    ErrorCode = "PROFILE_NOT_FOUND"
	CodeProfileUnavailable ErrorCode = "PROFILE_TEMPORARILY_UNAVAILABLE"
	CodeInternal           ErrorCode = "INTERNAL_ERROR"
)

type RecoveryAction string

const (
	ActionRetry             RecoveryAction = "retry"
	ActionDegrade           RecoveryAction = "degrade"
	ActionReturnPublicError RecoveryAction = "return_public_error"
	ActionEscalate          RecoveryAction = "escalate"
)

type AppError struct {
	Code    ErrorCode
	Message string
	Cause   error
}

func (e *AppError) Error() string {
	if e.Cause == nil {
		return fmt.Sprintf("%s: %s", e.Code, e.Message)
	}
	return fmt.Sprintf("%s: %s: %v", e.Code, e.Message, e.Cause)
}

func (e *AppError) Unwrap() error { return e.Cause }

type RecoveryDecision struct {
	Action        RecoveryAction
	PublicCode    ErrorCode
	PublicMessage string
	Retryable     bool
	Degraded      bool
}

var decisionTable = map[ErrorCode]RecoveryDecision{
	CodeProfileNotFound: {
		Action:        ActionReturnPublicError,
		PublicCode:    CodeProfileNotFound,
		PublicMessage: "profile not found",
	},
	CodeProfileUnavailable: {
		Action:        ActionRetry,
		PublicCode:    CodeProfileUnavailable,
		PublicMessage: "profile service is temporarily unavailable",
		Retryable:     true,
	},
	CodeInternal: {
		Action:        ActionEscalate,
		PublicCode:    CodeInternal,
		PublicMessage: "internal server error",
	},
}

func decideRecovery(err error) RecoveryDecision {
	var appErr *AppError
	if errors.As(err, &appErr) {
		if decision, ok := decisionTable[appErr.Code]; ok {
			return decision
		}
	}
	return decisionTable[CodeInternal]
}

func displayNameOrDegrade(err error) (string, RecoveryDecision, error) {
	var appErr *AppError
	if !errors.As(err, &appErr) || appErr.Code != CodeProfileNotFound {
		return "", RecoveryDecision{}, err
	}

	base := decideRecovery(err)
	return "anonymous", RecoveryDecision{
		Action:        ActionDegrade,
		PublicCode:    base.PublicCode,
		PublicMessage: base.PublicMessage,
		Degraded:      true,
	}, nil
}

func publicResponse(err error) map[string]string {
	decision := decideRecovery(err)
	return map[string]string{
		"code":    string(decision.PublicCode),
		"message": decision.PublicMessage,
	}
}

var (
	errNoRows      = errors.New("sql: no rows in result set")
	errProfileHost = errors.New("profile sdk timeout: host=10.0.0.8 trace=abc")
	errCorrupted   = errors.New("json decode failed at /var/lib/profiles/42.json")
)

func translateProfileError(err error) error {
	switch {
	case errors.Is(err, errNoRows):
		return &AppError{Code: CodeProfileNotFound, Message: "profile not found", Cause: err}
	case errors.Is(err, errProfileHost):
		return &AppError{Code: CodeProfileUnavailable, Message: "profile temporarily unavailable", Cause: err}
	default:
		return &AppError{Code: CodeInternal, Message: "internal server error", Cause: err}
	}
}

func must(condition bool, message string) {
	if !condition {
		panic(message)
	}
}

func main() {
	missing := translateProfileError(errNoRows)
	name, degradedDecision, degradeErr := displayNameOrDegrade(missing)
	must(degradeErr == nil, "missing profile should be degraded by this caller")
	must(name == "anonymous", "missing profile should use anonymous display name")
	must(degradedDecision.Action == ActionDegrade, "missing profile should be marked as degraded")
	must(degradedDecision.Degraded, "degraded decision should be observable")

	temporary := translateProfileError(errProfileHost)
	retryDecision := decideRecovery(temporary)
	must(retryDecision.Action == ActionRetry, "temporary profile error should be retryable")
	must(retryDecision.Retryable, "retryable flag should be explicit")

	response := fmt.Sprint(publicResponse(temporary))
	must(strings.Contains(response, string(CodeProfileUnavailable)), "public response should use domain code")
	must(!strings.Contains(response, "10.0.0.8"), "public response leaked host")
	must(!strings.Contains(response, "trace=abc"), "public response leaked trace")

	corrupted := translateProfileError(errCorrupted)
	must(decideRecovery(corrupted).Action == ActionEscalate, "corrupted profile should escalate")
	must(!strings.Contains(fmt.Sprint(publicResponse(corrupted)), "/var/lib"), "public response leaked file path")

	fmt.Println("error recovery decision table keeps Go actions explicit")
}
```

## 哪里容易错

1. **只靠分散的 `errors.Is` 判断**：service 决定重试，handler 决定错误码，另一个调用方又决定降级，最后没人能一眼看出完整恢复路径。
2. **新增领域错误但不更新决策表**：新错误一路落到默认 500，或被某个调用方误判成可降级。
3. **把降级藏在 repository / client 里**：底层 adapter 返回空对象会让调用方无法区分“数据不存在”和“依赖故障”。
4. **公开响应拼接 `err.Error()`**：`%w` / `Unwrap` 应该保留给日志和排障，公开 `code` / `message` 只读决策表里的安全字段。

## 一句话总结

Go 的错误恢复不要散落在多个 `if err != nil` 分支里；用一张决策表把领域错误、恢复动作、重试/降级标记和对外错误码串起来，调用方再按业务场景选择是否执行降级。

## 延伸阅读

- Go 显式重试：[`retry-policy-explicit-not-hidden-loop.md`](retry-policy-explicit-not-hidden-loop.md)
- Go 调用方降级：[`degradation-strategy-at-caller-not-callee.md`](degradation-strategy-at-caller-not-callee.md)
- Go 对外错误码：[`external-error-codes-domain-defined-not-leaked.md`](external-error-codes-domain-defined-not-leaked.md)
- Python 决策表对照：[`../python/error-recovery-path-needs-one-decision-table.md`](../python/error-recovery-path-needs-one-decision-table.md)
