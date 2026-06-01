# `Result` 表达“可能失败且有原因”

**问题**：如何把错误从底层传到上层，同时保留失败原因？

**要点**：

- `Result<T, E>` 是成功值或错误值，调用方必须显式处理。
- `?` 用于向上传播错误，适合把“我处理不了”的失败交给上层。
- 应用层可以用统一错误类型，库层避免随意吞错误或只返回字符串。
- 错误类型应该让调用方能分类：例如区分 I/O 错误和配置格式错误。

**示例**：

```rust
use std::fmt;
use std::fs;
use std::io;
use std::path::Path;

#[derive(Debug, PartialEq, Eq)]
struct Config {
    host: String,
    port: u16,
}

#[derive(Debug)]
enum ConfigError {
    Io(io::Error),
    InvalidFormat { line: String },
    InvalidPort { value: String },
}

impl From<io::Error> for ConfigError {
    fn from(error: io::Error) -> Self {
        ConfigError::Io(error)
    }
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ConfigError::Io(error) => write!(f, "read config failed: {error}"),
            ConfigError::InvalidFormat { line } => write!(f, "invalid config line: {line}"),
            ConfigError::InvalidPort { value } => write!(f, "invalid port: {value}"),
        }
    }
}

fn load_config(path: &Path) -> Result<Config, ConfigError> {
    let content = fs::read_to_string(path)?;
    parse_config(&content)
}

fn parse_config(content: &str) -> Result<Config, ConfigError> {
    let mut host = None;
    let mut port = None;

    for raw_line in content.lines() {
        let line = raw_line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        let (key, value) = line
            .split_once('=')
            .ok_or_else(|| ConfigError::InvalidFormat { line: line.to_string() })?;

        match key.trim() {
            "host" => host = Some(value.trim().to_string()),
            "port" => {
                let value = value.trim();
                port = Some(
                    value
                        .parse::<u16>()
                        .map_err(|_| ConfigError::InvalidPort { value: value.to_string() })?,
                );
            }
            _ => return Err(ConfigError::InvalidFormat { line: line.to_string() }),
        }
    }

    let host = host.ok_or_else(|| ConfigError::InvalidFormat { line: "missing host".into() })?;
    let port = port.ok_or_else(|| ConfigError::InvalidFormat { line: "missing port".into() })?;

    Ok(Config { host, port })
}

fn main() -> Result<(), ConfigError> {
    let dir = std::env::temp_dir();
    let valid_path = dir.join("tech-card-valid-config.txt");
    let invalid_path = dir.join("tech-card-invalid-config.txt");
    let missing_path = dir.join("tech-card-missing-config.txt");

    fs::write(&valid_path, "host=127.0.0.1\nport=8080\n")?;
    fs::write(&invalid_path, "host=127.0.0.1\nport=eighty\n")?;
    let _ = fs::remove_file(&missing_path);

    let config = load_config(&valid_path)?;
    assert_eq!(config, Config { host: "127.0.0.1".into(), port: 8080 });

    match load_config(&invalid_path) {
        Err(ConfigError::InvalidPort { value }) => assert_eq!(value, "eighty"),
        other => panic!("expected invalid port error, got {:?}", other),
    }

    match load_config(&missing_path) {
        Err(ConfigError::Io(error)) => assert_eq!(error.kind(), io::ErrorKind::NotFound),
        other => panic!("expected missing file error, got {:?}", other),
    }

    let _ = fs::remove_file(valid_path);
    let _ = fs::remove_file(invalid_path);

    println!("loaded config for {}:{}", config.host, config.port);
    println!("result demo done");
    Ok(())
}
```

**坑**：把所有错误转成字符串会丢失类型信息，后续难以分类处理；反过来，把底层错误类型原样泄露给所有调用方，也会让接口过早绑定实现细节。

**检查**：调用方能否区分“文件不存在”“权限不足”“格式错误”？如果能用 `match` 或 `error.kind()` 做可靠分支，错误类型通常就够用。
