# HTTP handler 不要把内部错误直接暴露给客户端

## 什么时候用

当 HTTP handler 调用业务逻辑、数据库或外部服务，并把错误原样写入响应体或日志时。内部错误消息通常包含堆栈、SQL、文件路径或第三方凭证，直接返回会泄露实现细节并增加攻击面。

## 怎么写

```go
// error.go — 把业务错误和内部错误分开
package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
)

// UserError 是可以安全返回给客户端的业务错误。
type UserError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func (e *UserError) Error() string {
	return fmt.Sprintf("user error %d: %s", e.Code, e.Message)
}

// internalError 把原始错误记录到日志，返回一个安全的 500 响应。
func internalError(w http.ResponseWriter, err error) {
	// 在真实项目中用 structured logger 记录完整错误。
	fmt.Printf("internal error: %v\n", err)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusInternalServerError)
	json.NewEncoder(w).Encode(map[string]string{
		"error": "internal server error",
	})
}

// userErrorResponse 把 UserError 写成 JSON 响应。
func userErrorResponse(w http.ResponseWriter, ue *UserError) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(ue.Code)
	json.NewEncoder(w).Encode(ue)
}

// --- 业务层 ---

type Product struct {
	ID    string  `json:"id"`
	Name  string  `json:"name"`
	Price float64 `json:"price"`
}

var (
	ErrNotFound = &UserError{Code: 404, Message: "product not found"}
	ErrInvalid  = &UserError{Code: 400, Message: "invalid product id"}
)

func findProduct(id string) (*Product, error) {
	if id == "" {
		return nil, ErrInvalid
	}
	if id != "p-001" {
		return nil, ErrNotFound
	}
	// 模拟数据库查询成功
	return &Product{ID: id, Name: "Notebook", Price: 29.9}, nil
}

// --- Handler ---

func getProductHandler(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")

	product, err := findProduct(id)
	if err != nil {
		var ue *UserError
		if errors.As(err, &ue) {
			userErrorResponse(w, ue)
			return
		}
		// 不是 UserError → 内部错误，不暴露原始信息。
		internalError(w, err)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(product)
}

func main() {
	recorder := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodGet, "/product?id=p-001", nil)
	getProductHandler(recorder, request)
	if recorder.Code != http.StatusOK {
		panic("expected product response")
	}
	if strings.Contains(recorder.Body.String(), "password") {
		panic("internal field leaked")
	}

	recorder = httptest.NewRecorder()
	request = httptest.NewRequest(http.MethodGet, "/product?id=missing", nil)
	getProductHandler(recorder, request)
	if recorder.Code != http.StatusNotFound {
		panic("expected safe user error")
	}
	if !strings.Contains(recorder.Body.String(), "product not found") {
		panic("expected user-facing message")
	}
}
```

## 哪里容易错

1. **把 `err.Error()` 写进响应体**：数据库连接失败、文件不存在、权限不足等消息不应该离开服务端。
2. **只用 `http.Error()` 返回所有错误**：它把 `err.Error()` 原样输出，适合开发调试但不适合生产。
3. **用同一个 `error` 类型表达所有业务错误**：无法区分"客户端参数错误"和"服务端数据库挂了"，应该在 handler 层用 `errors.As` 分流。
4. **忘了记录内部错误**：对外隐藏错误是对的，但如果也不记日志，排障时就找不到原因。

## 一句话总结

HTTP handler 是外部错误的出口、内部错误的日志点；`UserError` 可以安全返回，其余一律记日志并返回 500。
