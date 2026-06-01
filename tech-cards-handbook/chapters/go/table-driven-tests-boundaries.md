# 表格驱动测试让边界更清楚

**问题**：多个输入输出组合如何写得清楚？

**要点**：

- 把用例放进 slice，并让每个用例都有 `name`。
- 用例里同时表达输入、期望输出，以及是否期望错误。
- 失败信息要包含输入、实际结果和期望结果，让排查不依赖重新跑调试器。

**示例**：

```go
package email

import (
	"errors"
	"strings"
	"testing"
)

var ErrInvalidEmail = errors.New("invalid email")

func NormalizeEmail(in string) (string, error) {
	email := strings.ToLower(strings.TrimSpace(in))
	if email == "" || !strings.Contains(email, "@") {
		return "", ErrInvalidEmail
	}
	return email, nil
}

func TestNormalizeEmail(t *testing.T) {
	tests := []struct {
		name    string
		in      string
		want    string
		wantErr error
	}{
		{name: "trim and lower", in: "  A@EXAMPLE.COM ", want: "a@example.com"},
		{name: "already clean", in: "b@example.com", want: "b@example.com"},
		{name: "empty is invalid", in: "   ", wantErr: ErrInvalidEmail},
		{name: "missing at sign", in: "alice.example.com", wantErr: ErrInvalidEmail},
	}

	for _, tt := range tests {
		tt := tt // 兼容并行子测试和旧版 Go 的循环变量捕获习惯。
		t.Run(tt.name, func(t *testing.T) {
			got, err := NormalizeEmail(tt.in)

			if !errors.Is(err, tt.wantErr) {
				t.Fatalf("NormalizeEmail(%q) error=%v, want %v", tt.in, err, tt.wantErr)
			}
			if got != tt.want {
				t.Fatalf("NormalizeEmail(%q)=%q, want %q", tt.in, got, tt.want)
			}
		})
	}
}
```

**坑**：并行子测试里直接捕获循环变量，在旧写法中容易出错；需要显式重新绑定。表格里不要只放“正常路径”，否则边界行为会散落到手写分支里，测试会重新变得难读。

**检查**：新增边界条件是否只需要加一行测试数据？失败日志是否能直接指出是哪组输入出了问题？
