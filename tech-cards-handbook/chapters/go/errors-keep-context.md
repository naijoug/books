# 错误要保留上下文

**问题**：日志里只有 `not found`，怎么知道是哪一步失败？

**要点**：

- 用 `%w` 包装原始错误。
- 上层添加业务上下文。
- 判断错误类型时用 `errors.Is` 或 `errors.As`。

**示例**：

```go
func LoadConfig(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read config %s: %w", path, err)
	}
	cfg, err := parseConfig(data)
	if err != nil {
		return nil, fmt.Errorf("parse config %s: %w", path, err)
	}
	return cfg, nil
}
```

**坑**：`fmt.Errorf("failed: %v", err)` 会丢失错误链，后续无法用 `errors.Is` 判断。

**检查**：错误信息是否包含“做什么、对谁做、原始错误是什么”？
