# `never` 穷尽检查防止漏掉状态分支

**问题**：联合类型状态新增了一个分支，旧的 `switch` 代码没有同步更新，怎样让编译器立刻报错？

**要点**：

- `never` 表示“不可能出现的值”；如果所有联合类型分支都处理完，剩余变量会被缩窄为 `never`。
- 在 `switch` 的 `default` 分支调用 `assertNever(value: never)`，可以把遗漏分支变成编译错误。
- `assertNever` 不只是运行时兜底，更是给未来维护者的编译期提醒。
- 它特别适合任务状态、agent 步骤、支付状态、审批流这类“枚举会继续增长”的领域模型。

**示例**：

```typescript
type AgentStep =
  | { kind: "plan"; goal: string }
  | { kind: "act"; command: string }
  | { kind: "verify"; check: string }
  | { kind: "handoff"; note: string };

function assertNever(value: never): never {
  throw new Error(`unhandled agent step: ${JSON.stringify(value)}`);
}

function describeStep(step: AgentStep): string {
  switch (step.kind) {
    case "plan":
      return `规划：${step.goal}`;
    case "act":
      return `执行：${step.command}`;
    case "verify":
      return `验证：${step.check}`;
    case "handoff":
      return `交接：${step.note}`;
    default:
      return assertNever(step);
  }
}

const nextStep: AgentStep = {
  kind: "verify",
  check: "run unit tests before reporting done",
};

console.log(describeStep(nextStep));
```

最小验证：把上面的代码保存为 `never-exhaustive-state-checks.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom never-exhaustive-state-checks.ts`；如果没有类型错误，说明当前 `AgentStep` 的所有分支都已处理。可以再给 `AgentStep` 增加 `| { kind: "review"; reviewer: string }`，但不修改 `describeStep`，此时 `assertNever(step)` 会报错，因为 `step` 不再是 `never`。

**坑**：不要用 `default: return "unknown"` 或 `const _ignored = step as never` 来压掉错误。这样会让新增状态悄悄走兜底分支，直到线上出现错误文案、遗漏动作或错误流转。

**检查**：每次写 discriminated union 的 `switch` 时，问自己：未来新增一个 `kind/status/type`，我希望旧代码静默降级，还是希望编译器强制我补分支？后者就用 `assertNever`。
