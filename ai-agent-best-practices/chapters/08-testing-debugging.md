# AI Agent 最佳实践指南

## 第八章：测试与调试 —— 确保 Agent 可靠工作

> "Agent 开发中，测试比开发更重要。"

---

## 8.1 为什么需要专门的测试？

### 8.1.1 Agent 测试的挑战

| 挑战 | 说明 |
|--------|------|
| 非确定性 | 同样的输入可能有不同输出 |
| 长链路 | 任务可能需要很多步骤 |
| 外部依赖 | 工具调用、网络都可能失败 |
| 主观判断 | 什么是"好"的输出？ |

### 8.1.2 测试金字塔

```
        /\
       /E2E\        端到端测试（少量）
      /------\
     / 集成测试 \    集成测试（适中）
    /------------\
   /   单元测试   \   单元测试（大量）
  ------------------
```

---

## 8.2 单元测试

### 8.2.1 测试单个组件

```python
# 测试工具
def test_calculator_tool():
    tool = CalculatorTool()
    result = tool.run("2 + 2")
    assert result.success == True
    assert result.output == "4"

# 测试记忆
def test_memory_retrieval():
    memory = VectorStoreMemory()
    memory.add("用户喜欢咖啡")
    results = memory.retrieve("用户喜欢什么？")
    assert "咖啡" in results[0]

# 测试 Prompt
def test_prompt_formatting():
    prompt = AgentPrompt()
    formatted = prompt.format(question="你好")
    assert "Question: 你好" in formatted
```

---

## 8.3 集成测试

### 8.3.1 测试 Agent 流程

```python
def test_agent_with_tools():
    agent = create_agent(tools=[search_tool, calculator_tool])
    
    # 测试搜索
    result = agent.run("搜索今天的日期")
    assert "2026" in result
    
    # 测试计算
    result = agent.run("123 * 456")
    assert "56088" in result
```

---

## 8.4 端到端测试

### 8.4.1 真实场景测试

```python
def test_book_travel_agent():
    agent = create_travel_agent()
    
    # 完整流程测试
    result = agent.run("""
        帮我订一张下周去北京的机票：
        - 日期：3月10日
        - 预算：2000元以内
        - 时间：上午出发
    """)
    
    # 验证结果
    assert "航班" in result
    assert "价格" in result
```

---

## 8.5 评估指标

### 8.5.1 关键指标

| 指标 | 说明 | 目标 |
|------|------|------|
| 任务成功率 | 成功完成的任务比例 | >90% |
| 平均步骤数 | 完成任务平均步骤 | <10 步 |
| 工具使用率 | 工具使用合理性 | 合理选择 |
| 用户满意度 | 用户反馈评分 | >4.0 |
| 错误恢复率 | 从错误中恢复的能力 | >80% |

---

## 8.6 调试技巧

### 8.6.1 可观测性

```python
# 记录一切
agent = create_agent(
    verbose=True,  # 详细日志
    trace_callback=langsmith_tracer  # 可视化追踪
)

# 检查思考过程
print(agent.last_thoughts)

# 检查工具调用
print(agent.tool_calls)
```

---

## 8.7 本章小结

✅ **学习要点**：
1. Agent 测试有独特的挑战
2. 测试金字塔：单元 → 集成 → 端到端
3. 关键指标：成功率、步骤数、满意度
4. 可观测性是调试的关键

🚀 **下一步**：
下一章我们将探讨部署与监控——如何让 Agent 在生产环境稳定运行。

---

*本章结束* 📖
