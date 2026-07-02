# 统一 preflight wrapper 防止命令漂移，不要靠记忆拼验证清单

**问题**：Agent 连续维护文档、索引或样本包时，验证命令会逐轮增长：先跑链接扫描，再跑索引校验，再补回归测试。如何避免下一轮只记得其中一条命令，导致报告里看似验证充分、实际漏跑关键检查？

**要点**：

- 把稳定的验证组合收束成一个 wrapper 命令，让“应该一起跑”的检查共享入口，而不是散落在 notebook、README 和最终报告里。
- wrapper 的职责是编排已有检查：先跑 verifier 自身的回归 fixture，再跑全量 manuscript 检查；不要把业务规则、修复逻辑和临时实验塞进去。
- wrapper 要保留每一步的可见输出和失败标签，让失败能定位到“链接回归”“索引回归”“全量链接”或“全量索引”，而不是只返回一个模糊失败。
- 为常见低风险改动提供显式快速模式，例如只跑全量检查，但默认路径仍应覆盖回归测试，避免长期维护中测试被遗忘。
- wrapper 自己也要有最小回归测试：默认顺序、快速模式跳过范围、子命令失败后立即停止，至少这三件事不能靠人工读代码确认。
- 文档入口只写 wrapper 命令和边界说明；底层命令留在脚本里，减少多处文档同步成本。

**示例**：

```text
场景：tech-cards-handbook 维护入口和样本包链接越来越多。

原始验证清单：
1. python3 scripts/test_verify_tech_cards_links.py
2. python3 scripts/test_verify_tech_cards_index.py
3. python3 scripts/verify_tech_cards_links.py
4. python3 scripts/verify_tech_cards_index.py

统一后：
- 默认：python3 scripts/verify_tech_cards.py
- 普通文案快速检查：python3 scripts/verify_tech_cards.py --full-only
- wrapper 变更自测：python3 scripts/test_verify_tech_cards.py

最终报告写：
- 运行统一 preflight，4 个 step 均通过；快速模式只用于未改 verifier 脚本的普通文案变更。
```

一个好的 wrapper 输出应该像命令梯，而不是黑盒：

```text
==> link verifier regression: ...
==> index verifier regression: ...
==> link verifier: ...
==> index verifier: ...
tech-cards verification suite ok: 4 step(s)
```

**坑**：

- wrapper 只打印“全部成功”，不暴露每个子命令；失败时下一轮无法判断该缩小到哪一步。
- wrapper 悄悄吞掉子命令 exit code，导致某个 verifier 失败后仍继续报告成功。
- wrapper 没有自己的测试，后来新增快速模式或重排步骤时，只能靠最终输出猜测是否漏跑。
- README 同时维护 wrapper 命令和底层命令列表，几轮后两边漂移。
- 把 wrapper 做成通用任务运行器，混入格式化、生成、提交、发布等副作用；preflight 应先保持只读和可重复。
- 快速模式没有命名边界，导致大家默认跳过回归 fixture。

**检查**：如果一个仓库的验证说明需要读者连续复制三条以上命令，先问这些命令是否代表同一个交付契约。若是，就把它们包成 wrapper，并确认：默认模式覆盖回归与全量检查；快速模式名字写清跳过了什么；失败输出能定位到具体 step；wrapper 变更有顺序和失败停止测试；文档入口不再重复维护底层命令清单。
