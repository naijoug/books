# 断言函数让边界错误提前失败

**问题**：类型守卫适合写在 `if` 分支里，但有些边界代码希望“检查不通过就直接失败”，并让后续代码拿到已缩窄类型，应该怎么写？

**要点**：

- 断言函数返回类型写成 `asserts value is T`，表示函数返回后 `value` 已经是 `T`。
- 断言函数应该在检查失败时抛出明确错误；不要静默返回，也不要只做类型断言。
- 它适合 CLI 参数、配置文件、agent 工具调用结果、测试 fixture 等“错了就不该继续”的入口。
- 守卫回答“是不是”，断言回答“必须是”；业务函数可以在断言之后直接使用领域类型。

**示例**：

```typescript
type AgentConfig = {
  model: string;
  maxSteps: number;
  tools: string[];
};

function assertAgentConfig(value: unknown): asserts value is AgentConfig {
  if (typeof value !== "object" || value === null) {
    throw new Error("config must be an object");
  }

  const record = value as Record<string, unknown>;
  if (typeof record.model !== "string" || record.model.length === 0) {
    throw new Error("config.model must be a non-empty string");
  }
  if (
    typeof record.maxSteps !== "number" ||
    !Number.isInteger(record.maxSteps) ||
    record.maxSteps <= 0
  ) {
    throw new Error("config.maxSteps must be a positive integer");
  }
  if (!Array.isArray(record.tools) || !record.tools.every((tool) => typeof tool === "string")) {
    throw new Error("config.tools must be a string array");
  }
}

function startAgent(rawConfig: unknown): string {
  assertAgentConfig(rawConfig);

  const toolList = rawConfig.tools.join(", ");
  return `run ${rawConfig.model} for ${rawConfig.maxSteps} steps with ${toolList}`;
}

console.log(startAgent({ model: "hermes", maxSteps: 8, tools: ["search", "shell"] }));
```

最小验证：把上面的代码保存为 `assertion-functions-fail-fast-boundaries.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom assertion-functions-fail-fast-boundaries.ts`；如果没有类型错误，说明 `assertAgentConfig(rawConfig)` 之后 `rawConfig` 已经被缩窄为 `AgentConfig`。

**坑**：不要写成 `function assertX(value: unknown): asserts value is X { return; }`。这会骗过编译器，却把运行时错误推迟到业务逻辑深处。断言函数的价值在于“失败尽早、错误明确”。

**检查**：遇到外部输入时问自己：如果格式不对，程序应该继续走降级分支，还是应该立刻失败？前者用类型守卫，后者用断言函数。
