# 类型守卫把外部输入缩窄成领域对象

**问题**：从 API、表单、消息队列或 agent 工具结果拿到的数据只是 `unknown`，怎样在进入业务逻辑前确认它真的符合领域对象结构？

**要点**：

- 类型守卫函数返回 `value is T`，让 TypeScript 在 `if` 分支内自动缩窄类型。
- 守卫内部要做运行时检查：先确认是非空对象，再逐个检查关键字段。
- 守卫适合放在系统边界；业务函数只接收已经缩窄后的领域类型。
- 对复杂对象优先检查业务必须字段，不要把类型守卫写成“永远相信输入”的类型断言。

**示例**：

```typescript
type ToolResult = {
  id: string;
  status: "ok" | "failed";
  summary: string;
};

function isToolResult(value: unknown): value is ToolResult {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const record = value as Record<string, unknown>;
  return (
    typeof record.id === "string" &&
    (record.status === "ok" || record.status === "failed") &&
    typeof record.summary === "string"
  );
}

function renderToolResult(value: unknown): string {
  if (!isToolResult(value)) {
    return "工具结果格式不正确，暂不进入业务处理";
  }

  return `${value.id}: ${value.status} - ${value.summary}`;
}

console.log(renderToolResult({ id: "search-1", status: "ok", summary: "found 3 docs" }));
console.log(renderToolResult({ id: "search-2", status: "pending", summary: "waiting" }));
```

最小验证：把上面的代码保存为 `type-guards-narrow-domain-inputs.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom type-guards-narrow-domain-inputs.ts`；如果没有类型错误，说明业务分支只在守卫通过后访问领域字段。

**坑**：不要把守卫写成 `return true` 或 `return value as ToolResult` 这种“伪检查”。那只是换了一个名字做类型断言，运行时仍可能把错误 payload 送进业务逻辑。

**检查**：每个系统边界至少回答三个问题：输入最初是否是 `unknown`？守卫是否检查了必要字段？业务函数是否只接收守卫通过后的类型？
