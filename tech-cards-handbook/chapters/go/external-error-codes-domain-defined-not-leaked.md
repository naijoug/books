# 对外错误码应由领域定义，而不是从基础设施泄漏

## 什么时候用

当 handler、CLI 或 webhook 需要把错误返回给外部调用方时。数据库 SQL state、驱动错误类型、第三方 SDK code 和内部文件路径都适合进入日志与 tracing，不适合直接成为 API 契约。外部契约应该使用稳定的领域错误码，例如 `USER_NOT_FOUND`、`EMAIL_ALREADY_USED`、`SERVICE_OVERLOADED`。

## 怎么写

```go
// external-error-codes-domain-defined-not-leaked.go
package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strings"
)

type ErrorCode string

const (
	CodeUserNotFound     ErrorCode = "USER_NOT_FOUND"
	CodeEmailAlreadyUsed ErrorCode = "EMAIL_ALREADY_USED"
	CodeInternal         ErrorCode = "INTERNAL_ERROR"
)

type AppError struct {
	Code    ErrorCode
	Message string
	Cause   error
}

func (e *AppError) Error() string {
	if e.Cause == nil {
		return string(e.Code) + ": " + e.Message
	}
	return fmt.Sprintf("%s: %s: %v", e.Code, e.Message, e.Cause)
}

func (e *AppError) Unwrap() error { return e.Cause }

func publicResponse(err error) (int, []byte) {
	var appErr *AppError
	if !errors.As(err, &appErr) {
		appErr = &AppError{Code: CodeInternal, Message: "internal server error", Cause: err}
	}

	status := http.StatusInternalServerError
	switch appErr.Code {
	case CodeUserNotFound:
		status = http.StatusNotFound
	case CodeEmailAlreadyUsed:
		status = http.StatusConflict
	}

	body, encodeErr := json.Marshal(map[string]string{
		"code":    string(appErr.Code),
		"message": appErr.Message,
	})
	if encodeErr != nil {
		panic(encodeErr)
	}
	return status, body
}

var (
	errSQLNoRows   = errors.New("sql: no rows in result set")
	errSQLUnique   = errors.New("pq: SQLSTATE 23505 duplicate key value violates unique constraint users_email_key")
	errDriverPanic = errors.New("driver: connection reset by peer")
)

func findUser(id string) error {
	switch id {
	case "missing":
		return translateStorageError(errSQLNoRows)
	case "duplicate-email":
		return translateStorageError(errSQLUnique)
	case "broken-db":
		return translateStorageError(errDriverPanic)
	default:
		return nil
	}
}

func translateStorageError(err error) error {
	switch {
	case errors.Is(err, errSQLNoRows):
		return &AppError{Code: CodeUserNotFound, Message: "user not found", Cause: err}
	case errors.Is(err, errSQLUnique):
		return &AppError{Code: CodeEmailAlreadyUsed, Message: "email already used", Cause: err}
	default:
		return &AppError{Code: CodeInternal, Message: "internal server error", Cause: err}
	}
}

func main() {
	for _, id := range []string{"missing", "duplicate-email", "broken-db"} {
		err := findUser(id)
		status, body := publicResponse(err)
		fmt.Printf("%s -> %d %s\n", id, status, body)

		publicBody := string(body)
		if strings.Contains(publicBody, "SQLSTATE") || strings.Contains(publicBody, "users_email_key") || strings.Contains(publicBody, "connection reset") {
			panic("public response leaked infrastructure detail: " + publicBody)
		}
	}
}
```

## 哪里容易错

1. **把 SQL state 当成 API code**：`23505` 对数据库有意义，对客户端没有稳定业务语义；应该先翻译成 `EMAIL_ALREADY_USED`。
2. **在 handler 里到处写字符串**：`"not_found"`、`"user missing"`、`"no rows"` 分散后很难保证兼容性；用领域枚举集中定义。
3. **对外隐藏错误时也丢掉内部根因**：公开响应不能泄漏底层细节，但内部错误仍要通过 `%w` / `Unwrap` 保留给日志、告警和排障。
4. **让 adapter code 进入领域层**：repository 可以识别 SQL state，领域 service 只应该看到 `AppError.Code` 这类业务可理解分类。

## 一句话总结

对外错误码是产品契约，不是基础设施日志；adapter 负责把底层错误翻译成领域错误码，handler 只输出稳定 code 和安全 message。
