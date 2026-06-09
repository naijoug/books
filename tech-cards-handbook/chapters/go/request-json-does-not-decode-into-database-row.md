# 请求 JSON 不直接反序列化到数据库 row

## 什么时候用

当 `POST` / `PATCH` handler 收到 JSON 后，想直接 `json.NewDecoder(r.Body).Decode(&UserRow{})`，再把 row 交给 repository 保存时。请求 JSON 是外部输入契约，数据库 row 是持久化结构，直接绑定会把客户端可写字段、数据库列和业务规则搅在一起。

## 怎么写

```go
// handler.go — 请求 DTO 先转成 command，再由业务层决定可更新字段
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
)

// UserRow 是数据库结构，包含客户端绝不能写入的字段。
type UserRow struct {
	ID           int
	Email        string
	DisplayName  string
	PasswordHash string
	Role         string
	UpdatedBy    string
}

// UpdateUserRequest 是 HTTP 输入契约，只描述这个接口允许客户端提交什么。
type UpdateUserRequest struct {
	DisplayName string `json:"displayName"`
}

// UpdateUserCommand 是业务动作，不带 HTTP tag，也不暴露数据库列。
type UpdateUserCommand struct {
	UserID      int
	DisplayName string
	Actor       string
}

type UserRepository interface {
	FindByID(id int) (UserRow, error)
	Save(row UserRow) error
}

type MemoryUserRepository struct {
	row UserRow
}

func (repo *MemoryUserRepository) FindByID(id int) (UserRow, error) {
	if repo.row.ID != id {
		return UserRow{}, fmt.Errorf("user row not found: %d", id)
	}
	return repo.row, nil
}

func (repo *MemoryUserRepository) Save(row UserRow) error {
	repo.row = row
	return nil
}

func parseUpdateUserRequest(body *strings.Reader) (UpdateUserRequest, error) {
	var request UpdateUserRequest
	if err := json.NewDecoder(body).Decode(&request); err != nil {
		return UpdateUserRequest{}, fmt.Errorf("decode update user request: %w", err)
	}
	request.DisplayName = strings.TrimSpace(request.DisplayName)
	if request.DisplayName == "" {
		return UpdateUserRequest{}, fmt.Errorf("displayName is required")
	}
	return request, nil
}

func requestToCommand(userID int, actor string, request UpdateUserRequest) UpdateUserCommand {
	return UpdateUserCommand{
		UserID:      userID,
		DisplayName: request.DisplayName,
		Actor:       actor,
	}
}

func updateUser(repo UserRepository, command UpdateUserCommand) error {
	row, err := repo.FindByID(command.UserID)
	if err != nil {
		return err
	}

	// 业务层只更新本动作允许修改的字段。
	row.DisplayName = command.DisplayName
	row.UpdatedBy = command.Actor
	return repo.Save(row)
}

func updateUserHandler(repo UserRepository) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		request, err := parseUpdateUserRequest(strings.NewReader(readBody(r)))
		if err != nil {
			http.Error(w, "invalid request", http.StatusBadRequest)
			return
		}

		command := requestToCommand(1, "admin@example.com", request)
		if err := updateUser(repo, command); err != nil {
			http.Error(w, "user not found", http.StatusNotFound)
			return
		}

		w.WriteHeader(http.StatusNoContent)
	}
}

func readBody(r *http.Request) string {
	data, _ := io.ReadAll(r.Body)
	return string(data)
}

func main() {
	repo := &MemoryUserRepository{row: UserRow{
		ID:           1,
		Email:        "ada@example.com",
		DisplayName:  "Ada",
		PasswordHash: "argon2$secret",
		Role:         "admin",
	}}

	body := `{"displayName":"Ada Lovelace","role":"owner","passwordHash":"plain"}`
	request := httptest.NewRequest(http.MethodPatch, "/users/1", strings.NewReader(body))
	recorder := httptest.NewRecorder()

	updateUserHandler(repo)(recorder, request)

	fmt.Println(recorder.Code)
	fmt.Println(repo.row.DisplayName)
	fmt.Println(repo.row.Role)
	fmt.Println(repo.row.PasswordHash)
}
```

## 哪里容易错

1. **直接 decode 到数据库 row**：客户端可能提交 `role`、`passwordHash`、`deletedAt` 等字段，一旦 row 带 `json` tag 或后续复用就容易越权写入。
2. **用 `omitempty` 当权限控制**：字段是否为空不是“是否允许修改”的规则；允许更新的字段应由 request DTO 和 command 明确列出。
3. **handler 直接拼数据库更新语句**：输入校验、授权、字段归一化和存储细节会挤在 handler 里，难以测试。
4. **把 HTTP tag 加到领域模型或 row 上**：这会让外部契约反向决定内部结构，后续重命名字段时改动面会扩大。

## 一句话总结

请求 JSON 先进入输入 DTO，再转成业务 command；数据库 row 只在 repository 边界内出现，客户端永远不能决定哪些数据库列可写。
