# AI Agent 最佳实践指南

## 第七章：工具集成架构 —— 让 Agent 安全地连接外部系统

> "没有工具的 Agent 就像没有手的人——想法很多，但什么都做不了。"

---

## 7.1 工具的重要性

### 7.1.1 LLM 的局限性

| 局限性 | 说明 |
|--------|------|
| 知识截止 | 训练数据有截止日期 |
| 实时信息 | 不知道当前发生的事 |
| 计算能力 | 数学计算可能出错 |
| 外部交互 | 无法直接操作外部系统 |
| 长期记忆 | 上下文窗口有限 |

### 7.1.2 工具让 Agent 变得强大

```
没有工具：
用户: 今天天气怎么样？
Agent: 抱歉，我无法访问实时数据...

有了工具：
用户: 今天天气怎么样？
Agent: [调用天气工具]
       → 获取天气数据
       → 分析结果
       → "今天晴天，温度 25°C"
```

---

## 7.2 工具的类型

### 7.2.1 信息获取类

| 工具 | 用途 | 示例 |
|------|------|------|
| 搜索 | 获取实时信息 | Google Search, Tavily |
| 浏览 | 访问网页 | Playwright, Puppeteer |
| 数据库 | 查询数据 | SQL, NoSQL |
| API | 调用服务 | REST, GraphQL |

### 7.2.2 计算处理类

| 工具 | 用途 | 示例 |
|------|------|------|
| 计算器 | 数学计算 | Python REPL |
| 代码执行 | 运行代码 | Jupyter, CodeRunner |
| 数据处理 | 转换数据 | Pandas, NumPy |

### 7.2.3 文件操作类

| 工具 | 用途 | 示例 |
|------|------|------|
| 读文件 | 读取内容 | FileReader |
| 写文件 | 保存内容 | FileWriter |
| 目录操作 | 管理文件 | FileSystem |

### 7.2.4 通信交互类

| 工具 | 用途 | 示例 |
|------|------|------|
| 邮件 | 发送邮件 | SMTP, Gmail API |
| 消息 | 发送通知 | Slack, Discord, Telegram |
| 会议 | 日程管理 | Google Calendar |

---

## 7.3 工具定义的最佳实践

### 7.3.1 好的工具描述

```
❌ 不好的描述：
"搜索工具"

✅ 好的描述：
"搜索工具 - 当你需要回答关于 2023 年之后的时事问题、
查询最新的产品价格、或获取你不知道的事实信息时使用。
输入应该是具体的搜索关键词，不要是完整的问题。"
```

### 7.3.2 工具接口设计

```python
from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class ToolResult:
    success: bool
    output: str
    error: str = None
    metadata: Dict[str, Any] = None

class BaseTool:
    name: str
    description: str
    
    def run(self, input: str) -> ToolResult:
        raise NotImplementedError
    
    def validate_input(self, input: str) -> bool:
        """验证输入是否有效"""
        return True
    
    def format_output(self, result: Any) -> str:
        """格式化输出"""
        return str(result)
```

---

## 7.4 工具执行的安全考虑

### 7.4.1 安全沙箱

```python
# ❌ 危险：直接执行
def run_code(code: str):
    exec(code)  # 太危险了！

# ✅ 安全：使用沙箱
def run_code_safe(code: str):
    # 1. 限制可用模块
    # 2. 限制执行时间
    # 3. 限制内存使用
    # 4. 限制网络访问
    # 5. 限制文件系统访问
    return sandboxed_exec(code)
```

### 7.4.2 权限最小化原则

```
工具权限设计：
- 只读 vs 读写：优先只读
- 临时 vs 持久：优先临时
- 受限 vs 完全：优先受限
- 人工确认 vs 自动执行：高危操作需要确认
```

### 7.4.3 为发布门禁预留工具安全元数据

第十章会把工具风险分级、权限网关、审计 trace 和发布安全门禁串成闭环。为了让后续测试和部署真正能拦住风险，第七章在定义工具时就要把安全元数据写清楚，而不是等上线前再补文档。

建议每个工具至少声明：

| 字段 | 作用 | 示例 |
|------|------|------|
| `risk_level` | 决定是否需要审批、灰度和安全回归 | `L0_readonly`、`L3_write`、`L4_irreversible` |
| `required_permission` | 交给服务端权限网关做确定性鉴权 | `crm:write`、`billing:refund` |
| `data_classes` | 判断参数和返回值是否需要脱敏 | `public`、`internal`、`personal`、`high_sensitive` |
| `side_effect` | 决定是否允许自动重试、重放和回滚 | `none`、`reversible_write`、`irreversible_write` |
| `audit_fields` | 指定 trace 中必须保留、必须脱敏和必须哈希的字段 | `tenant_id`、`args_hash`、`approval_id` |
| `rollback_strategy` | 供第九章发布回滚和第十章熔断 runbook 使用 | `disable_tool`、`readonly_fallback`、`manual_compensation` |

```yaml
name: refund_payment
description: "为已确认订单发起退款请求"
risk_level: L4_irreversible
required_permission: billing:refund
data_classes: [personal, payment]
side_effect: irreversible_write
audit_fields:
  keep: [tenant_id, order_id, approval_id, idempotency_key]
  hash: [payment_account]
  redact: [card_number, user_email]
rollback_strategy: manual_compensation
requires_approval: true
```

这些字段不是给模型“看起来更谨慎”的提示词，而是给运行时、测试集和发布流水线使用的硬约束：第八章可以据此生成安全回归集，第九章可以在灰度和回滚时关闭高风险工具，第十章可以把失败样本接入发布门禁与熔断 runbook。

---

## 7.5 工具选择与路由

### 7.5.1 智能工具选择

**问题**：工具太多，Agent 不知道选哪个

**解决方案**：

1. **动态工具过滤**：
   - 根据任务类型过滤工具
   - 根据上下文过滤工具

2. **工具描述优化**：
   - 清晰说明何时使用
   - 说明输入输出格式

3. **使用历史**：
   - 记录工具使用频率
   - 优先推荐常用工具

---

## 7.6 本章小结

✅ **学习要点**：
1. 工具让 Agent 突破 LLM 的局限性
2. 4 类工具：信息获取、计算处理、文件操作、通信交互
3. 工具描述要清晰、具体
4. 安全第一：沙箱、权限最小化、人工确认
5. 工具安全元数据要提前声明，方便安全回归集、发布门禁和熔断 runbook 使用
6. 智能工具选择：过滤、优化、历史记录

🚀 **下一步**：
下一章我们将探讨 Agent 的测试与调试——如何确保 Agent 可靠地工作。

---

**思考问题**：
1. 你的 Agent 需要哪些工具？
2. 如何确保工具的安全性？
3. 工具太多时，如何帮助 Agent 选择？

---

*本章结束* 📖
