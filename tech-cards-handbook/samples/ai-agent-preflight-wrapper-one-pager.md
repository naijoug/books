# AI Agent 统一 preflight wrapper 一页纸

用途：当一个仓库已经有多条稳定验证命令，并且最终报告经常要解释“我到底跑了哪几条”时，用这页纸把它们收束成一个只读、可重复、可测试的 wrapper。先读卡片 [`../chapters/ai-agent/unified-preflight-wrapper-prevents-command-drift.md`](../chapters/ai-agent/unified-preflight-wrapper-prevents-command-drift.md)，再复制下面的字段。

## 1. 是否应该包成 wrapper

| 判断项 | 填写 |
|---|---|
| 当前验证清单 | `<命令 1>` / `<命令 2>` / `<命令 3>` |
| 共同交付契约 | `<例如：证明 tech-cards 链接、索引和样本入口一致>` |
| 是否只读可重复 | `<是 / 否；若否，先拆出有副作用步骤>` |
| 是否已有绿色基线 | `<是 / 否；若否，先用 full proof baseline 处理>` |
| 漏跑代价 | `<下一轮最可能误报什么完成状态>` |
| 决策 | `<WRAP_NOW / KEEP_AS_LADDER / BASELINE_FIRST>` |

决策规则：
- `WRAP_NOW`：三条以上命令代表同一个交付契约，且全量基线已绿。
- `KEEP_AS_LADDER`：命令之间是探索顺序或风险递进，还没稳定成日常契约。
- `BASELINE_FIRST`：全量命令仍红，先回到 [`ai-agent-full-proof-baseline-one-pager.md`](ai-agent-full-proof-baseline-one-pager.md)。

## 2. wrapper 规格

```text
Wrapper name: <scripts/verify_xxx.py 或 package script>
Default mode:
1. <step label>: <command>
2. <step label>: <command>
3. <step label>: <command>

Fast mode name: <--full-only / --changed-only / 无>
Fast mode skips: <明确写跳过哪些 regression 或重型检查>
Stop rule: first failing step stops the wrapper and preserves child exit code
Output rule: print each step label before running it; success summary includes step count
Side-effect boundary: read-only; no formatting, generation, commit, publish, install
```

## 3. 最小回归测试

| 风险 | 测试断言 |
|---|---|
| 默认顺序漂移 | `<默认模式按 regression -> full proof 顺序调用>` |
| 快速模式边界变模糊 | `<fast mode 只跳过声明的步骤，不跳过全量基础检查>` |
| 子命令失败被吞 | `<模拟某一步失败时 wrapper 立即停止并返回非零>` |
| 输出不可定位 | `<stdout/stderr 包含失败 step label>` |

可复制测试任务：

```text
请为 wrapper 补最小测试，只覆盖编排契约：默认顺序、fast mode 跳过范围、失败即停和 step label 输出。不要在测试里重新验证业务规则；业务规则仍由底层 verifier 自己测试。
```

## 4. 文档入口降噪

把 README / AGENTS / notebook 里的底层命令清单替换成：

```text
常规验证：<wrapper 默认命令>
普通文案快速验证：<wrapper fast mode，如果适用>
wrapper 本身变更：<wrapper test 命令>
边界：wrapper 只证明 <基础契约>；渲染、插件、端到端流程仍需 <build/e2e 命令>。
```

不要同时维护“wrapper 命令 + 底层四条命令”的完整清单；底层顺序留在脚本和测试里。

## 5. notebook / 最终报告句式

```text
验证方式：运行 `<wrapper 默认命令>`，输出 `<step count>` 个 step 均通过；本轮未修改 wrapper，因此未单独运行 wrapper 编排测试。`<fast mode>` 仅用于普通文案改动，跳过 `<skipped steps>`。
```

如果 wrapper 失败：

```text
验证失败：`<wrapper command>` 在 `<step label>` 失败；本轮不扩大修复范围。下一步先打开 `<底层 verifier 或 fixture>`，确认是内容破损、checker 误报还是 wrapper 编排错误。
```

## 6. 收尾检查

- [ ] wrapper 默认模式覆盖 regression 与全量检查。
- [ ] fast mode 名字写清跳过范围。
- [ ] 失败输出能定位到具体 step label。
- [ ] wrapper 变更有编排测试。
- [ ] 文档入口只写 wrapper 命令、fast mode 和边界，不重复维护底层清单。
- [ ] 最终报告没有把 wrapper 能证明的基础契约夸大成 build / e2e 已通过。
