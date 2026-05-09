# AI Agent 最佳实践指南

## 第九章：部署与监控 —— 生产环境的稳定运行

> "开发完成只是开始，部署和监控才是长期挑战。"

---

## 9.1 部署架构

### 9.1.1 从开发到生产

```
开发环境
    ↓ (CI/CD)
测试环境
    ↓ (手动/自动审批)
预发布环境
    ↓ (灰度发布)
生产环境
```

### 9.1.2 容器化部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "agent_server.py"]
```

---

## 9.2 可观测性

### 9.2.1 三大支柱

| 支柱 | 工具 | 用途 |
|------|------|------|
| 日志 (Logging) | ELK, Loki | 记录事件 |
| 指标 (Metrics) | Prometheus | 监控数值 |
| 追踪 (Tracing) | Jaeger, OpenTelemetry | 追踪请求链路 |

---

## 9.3 监控告警

### 9.3.1 关键指标

```yaml
# Prometheus 告警规则
groups:
- name: agent_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(agent_errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Agent 错误率过高"
  
  - alert: SlowResponse
    expr: histogram_quantile(0.95, agent_response_time_seconds) > 10
    for: 5m
    labels:
      severity: warning
```

---

## 9.4 弹性与容错

### 9.4.1 重试与降级

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_agent_with_retry(input: str):
    return agent.run(input)

# 降级策略
def get_agent_response(input: str):
    try:
        return call_agent_with_retry(input)
    except Exception:
        # 降级到简单版本
        return simple_agent_response(input)
```

---

## 9.5 本章小结

✅ **学习要点**：
1. 部署架构：开发 → 测试 → 预发布 → 生产
2. 可观测性三大支柱：日志、指标、追踪
3. 监控告警：关键指标 + 及时通知
4. 弹性与容错：重试、降级、熔断

🚀 **下一步**：
下一章我们将探讨安全与伦理——负责任地开发 AI Agent。

---

*本章结束* 📖
