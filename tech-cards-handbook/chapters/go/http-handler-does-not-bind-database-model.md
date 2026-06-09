# HTTP handler 不直接绑定数据库模型

## 什么时候用

当 handler 从数据库查询出 `UserRow`、`ProductRecord` 这类持久化结构后，直接把它编码成 JSON 响应，或把请求 JSON 直接反序列化到数据库模型时。数据库模型表达存储细节，HTTP contract 表达外部契约，二者变化原因不同。

## 怎么写

```go
// handler.go — 把数据库 row、领域模型和响应 DTO 分开
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
)

// UserRow 是持久化结构，字段贴近数据库列。
type UserRow struct {
	ID           int
	Email        string
	PasswordHash string
	DisplayName  string
	DeletedAt    string
}

// User 是业务层真正关心的领域模型。
type User struct {
	ID          int
	Email       string
	DisplayName string
	Active      bool
}

// UserResponse 是 HTTP 响应契约，只放允许暴露给客户端的字段。
type UserResponse struct {
	ID          int    `json:"id"`
	Email       string `json:"email"`
	DisplayName string `json:"displayName"`
	Status      string `json:"status"`
}

type UserRepository interface {
	FindByID(id int) (UserRow, error)
}

type MemoryUserRepository struct{}

func (MemoryUserRepository) FindByID(id int) (UserRow, error) {
	if id != 1 {
		return UserRow{}, fmt.Errorf("user row not found: %d", id)
	}
	return UserRow{
		ID:           1,
		Email:        "ada@example.com",
		PasswordHash: "argon2$secret",
		DisplayName:  "Ada",
	}, nil
}

func rowToUser(row UserRow) User {
	return User{
		ID:          row.ID,
		Email:       strings.ToLower(row.Email),
		DisplayName: row.DisplayName,
		Active:      row.DeletedAt == "",
	}
}

func userToResponse(user User) UserResponse {
	status := "disabled"
	if user.Active {
		status = "active"
	}
	return UserResponse{
		ID:          user.ID,
		Email:       user.Email,
		DisplayName: user.DisplayName,
		Status:      status,
	}
}

func userHandler(repo UserRepository) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		row, err := repo.FindByID(1)
		if err != nil {
			http.Error(w, "user not found", http.StatusNotFound)
			return
		}

		user := rowToUser(row)
		response := userToResponse(user)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}
}

func main() {
	recorder := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodGet, "/users/1", nil)

	userHandler(MemoryUserRepository{})(recorder, request)

	fmt.Println(strings.TrimSpace(recorder.Body.String()))
}
```

## 哪里容易错

1. **把数据库 row 直接 `json.NewEncoder(w).Encode(row)`**：`PasswordHash`、软删除字段、审计字段都可能被带出服务边界。
2. **为了响应格式修改数据库模型**：给 row 加 `json` tag、格式化字段或可选字段，会让存储层被 HTTP contract 反向污染。
3. **请求体直接写入数据库 row**：外部输入应该先变成 command / form，再由 service 决定哪些字段允许更新。
4. **把 mapper 写成万能函数**：`rowToUser` 和 `userToResponse` 跨越两条不同边界，应分开命名、分开测试。

## 一句话总结

HTTP handler 只负责 adapter 边界：数据库 row 先进业务模型，业务模型再出响应 DTO，不让存储细节和外部契约互相污染。
