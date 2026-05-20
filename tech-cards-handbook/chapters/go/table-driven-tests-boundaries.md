# 表格驱动测试让边界更清楚

**问题**：多个输入输出组合如何写得清楚？

**要点**：

- 把用例放进 slice。
- 每个用例必须有 `name`。
- 失败时输出输入和期望结果。

**示例**：

```go
func TestNormalizeEmail(t *testing.T) {
	tests := []struct {
		name string
		in   string
		want string
	}{
		{"trim and lower", "  A@EXAMPLE.COM ", "a@example.com"},
		{"already clean", "b@example.com", "b@example.com"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NormalizeEmail(tt.in)
			if got != tt.want {
				t.Fatalf("NormalizeEmail(%q)=%q, want %q", tt.in, got, tt.want)
			}
		})
	}
}
```

**坑**：并行子测试里直接捕获循环变量，在旧写法中容易出错；需要显式重新绑定。

**检查**：新增边界条件是否只需要加一行测试数据？
