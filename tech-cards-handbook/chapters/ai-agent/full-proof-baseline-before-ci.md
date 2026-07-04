# 全量 proof 基线先变绿，再把它写进常规 preflight

**问题**：Agent 已经有一个轻量 proof checker 时，什么时候可以把它从“本轮辅助验证”升级成团队或仓库的常规 preflight / CI？

**要点**：

- 先跑一次全量 proof，拿到明确的红绿基线；不要在还存在已知旧问题时直接把命令写成“必跑项”。
- 如果全量 proof 失败，优先把失败分成三类：真实内容破损、checker 误报、暂不覆盖的集成边界；每类都要有下一步动作。
- 只有当全量 proof 从失败变为通过，且回归测试能锁住误报修复，才把它提升为更显眼的 preflight 说明或 CI 候选。
- 记录升级条件，而不是只记录命令：适用范围、已知不覆盖项、失败时谁负责修内容还是修 checker。
- 不要让全量 proof 替代窄范围 proof；日常小改仍先跑 changed-file proof，全量 proof 用来守住仓库级基线。

**示例**：

```text
场景：docs 仓库已有 scripts/check-markdown-proof.py。

错误升级方式：
- 直接在 AGENTS.md 写“每次都运行 python3 scripts/check-markdown-proof.py documents”。
- 但全量命令当前会失败，下一轮 Agent 只能在旧问题和本轮问题之间猜归属。

正确升级方式：
1. 改前跑：python3 scripts/check-markdown-proof.py documents。
2. 把失败清单分为：frontmatter 旧问题、链接旧问题、checker 误报。
3. 修真实内容破损；对 checker 误报补最小回归测试。
4. 改后跑：checker regression、全量 proof、changed-file proof。
5. 只有全量 proof 变绿后，才把它写入 AGENTS.md 或 CI 候选清单。
```

可复制的记录格式：

```text
Full proof baseline:
- command: python3 scripts/check-markdown-proof.py documents
- before: failed, N known issue(s)
- fixed as content: ...
- fixed as checker: ...
- after: passed, checked N file(s)
- regular use: changed-file proof for normal edits; full proof for checker/rules/broad structure changes
- not covered: renderer/sidebar/plugin behavior; run build when those paths change
```

**坑**：

- 全量 proof 还红时就写进“After Changes”，导致每轮都要解释历史失败，最后大家默认忽略它。
- 把 checker 误报当作文档问题硬改，损坏原本正确的外部链接或示例。
- 全量通过后删除 changed-file proof，让小改也必须承担仓库级扫描成本。
- 只在总结里说“全量 proof 已通过”，却不写失败前的清单和修复分类，下一轮无法判断这是新基线还是偶然通过。
- 把全量 proof 的通过误写成“构建通过”；渲染、sidebar、插件和主题行为仍需要 build 或人工预览覆盖。

**检查**：把 proof checker 升级为常规 preflight 前，必须能回答：全量命令改前是否跑过、失败项如何分类、哪些修复是内容修复、哪些修复有回归测试、改后全量 proof 输出是什么、日常 changed-file proof 和全量 proof 的分工是什么。
