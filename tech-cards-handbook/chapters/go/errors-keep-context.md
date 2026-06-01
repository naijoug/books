# 错误要保留上下文

**问题**：日志里只有 `not found`，怎么知道是哪一步失败？

**要点**：

- 用 `%w` 包装原始错误，让调用方还能沿着错误链判断根因。
- 每一层只补自己知道的上下文：做什么、对谁做、处在哪个业务步骤。
- 判断错误类型时用 `errors.Is` 或 `errors.As`，不要靠字符串匹配。

**示例**：

```go
package main

import (
	"errors"
	"fmt"
	"os"
	"strings"
)

var ErrInvalidConfig = errors.New("invalid config")

type Config struct {
	Name string
}

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

func parseConfig(data []byte) (*Config, error) {
	text := strings.TrimSpace(string(data))
	name, ok := strings.CutPrefix(text, "name=")
	if !ok || strings.TrimSpace(name) == "" {
		return nil, fmt.Errorf("%w: expected name=<value>", ErrInvalidConfig)
	}
	return &Config{Name: strings.TrimSpace(name)}, nil
}

func main() {
	_, err := LoadConfig("missing.toml")
	if err == nil {
		panic("expected missing file error")
	}
	if !errors.Is(err, os.ErrNotExist) {
		panic(fmt.Sprintf("want os.ErrNotExist in chain, got %v", err))
	}
	if !strings.Contains(err.Error(), "read config missing.toml") {
		panic(fmt.Sprintf("missing read context: %v", err))
	}

	file, err := os.CreateTemp("", "bad-config-*.toml")
	if err != nil {
		panic(err)
	}
	defer os.Remove(file.Name())
	if _, err := file.WriteString("title=demo"); err != nil {
		panic(err)
	}
	if err := file.Close(); err != nil {
		panic(err)
	}

	_, err = LoadConfig(file.Name())
	if err == nil {
		panic("expected invalid config error")
	}
	if !errors.Is(err, ErrInvalidConfig) {
		panic(fmt.Sprintf("want ErrInvalidConfig in chain, got %v", err))
	}
	if !strings.Contains(err.Error(), "parse config "+file.Name()) {
		panic(fmt.Sprintf("missing parse context: %v", err))
	}
}
```

**坑**：

- `fmt.Errorf("failed: %v", err)` 会丢失错误链，后续无法用 `errors.Is` 判断。
- 只在最底层打印日志、上层继续返回错误，容易造成重复日志；通常让边界层统一记录完整错误。
- 上下文不要变成噪音：`read config path: permission denied` 比 `failed to do thing: failed: permission denied` 更可查。

**检查**：错误信息是否包含“做什么、对谁做、原始错误是什么”？调用方是否仍能通过 `errors.Is` / `errors.As` 判断根因？
