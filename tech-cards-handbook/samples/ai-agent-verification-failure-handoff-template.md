# AI Agent 验证失败交接模板

用于短节拍 Agent 已完成一部分修改、但验证命令失败或无法执行的场景。目标不是把失败包装成“基本完成”，而是把可信结论、失败证据和下一轮第一条动作拆开，让下一位 Agent 能直接补验证或调整计划。

## 1. 先判断失败会不会改变结论

```text
验证命令：<命令或人工检查>
失败摘要：<关键错误，不贴无关长日志>
失败归属：<本轮改动 / 启动前 dirty path / 环境依赖 / 外部服务 / 信息缺口>
结论影响：<已验证结论是否降级；范围、顺序、目标或交接是否改变>
下一步第一条动作：<下一轮先运行/读取/确认什么>
```

如果失败来自本轮改动，优先修复或回滚；如果失败来自启动前 dirty path 或环境依赖，不要声称功能已完整验证，把它写成显式未验证项。

## 2. 最小交接块

```text
- 已验证：<通过的命令、结构断言、文件读取或人工可复核标准>。
- 未验证：<具体命令/交互/边界条件>；原因是 <失败归属或环境限制>。
- 结论措辞：本轮只能说 <可信结论>，不能说 <被失败阻断的更强结论>。
- 下一步：先 <第一条补验证动作>；若仍失败，则 <修复/缩小/切换/继续交接的规则>。
- 证据位置：<命令输出、diff、notebook 段落、相对路径>。
```

## 3. 三种常见写法

### A. 全量测试失败，但落在启动前 dirty 模块

```text
- 已验证：`git -C books diff --check -- tech-cards-handbook/samples/ai-agent-verification-failure-handoff-template.md` 通过；结构断言确认模板包含“已验证/未验证/结论措辞/下一步/证据位置”。
- 未验证：没有把 `loom` 的全量测试作为本轮完成证据；原因是 `loom` 启动前已有 staged/modified/untracked path，失败无法归因到本轮文档改动。
- 结论措辞：本轮只能说“新增并静态检查了交接模板”，不能说“已验证整个 workspace”。
- 下一步：若要继续 `loom`，先重新记录 `git -C loom status --short` 并判断 dirty path 归属；仍归属不明时不要接管。
- 证据位置：启动快照、收尾 status、`books` path-limited diff check。
```

### B. 构建依赖缺失，无法执行目标验证

```text
- 已验证：目标 Markdown 不含绝对路径，内部相对链接存在。
- 未验证：`npx -y pnpm@8.15.9 run docs:build` 未执行成功；原因是依赖安装被网络或 registry 限制阻断。
- 结论措辞：本轮只能说“文档结构和链接已静态检查”，不能说“站点构建通过”。
- 下一步：先在 `docs/web/vuepress` 运行 `npx -y pnpm@8.15.9 install --frozen-lockfile`，再运行 `npx -y pnpm@8.15.9 run docs:build`；若安装仍失败，把 registry/网络错误原文写入交接。
- 证据位置：安装命令输出、链接检查脚本输出、`docs` 收尾 status。
```

### C. 人工 UI 交互未覆盖

```text
- 已验证：单元测试和静态检查通过；相关 reducer/utility 的输入输出已用测试覆盖。
- 未验证：没有在真实桌面应用中手工点击设置页、任务详情和日志过滤；原因是本轮未启动 GUI。
- 结论措辞：本轮只能说“逻辑层已验证”，不能说“交互体验已验证”。
- 下一步：启动应用，按“打开设置 -> 修改终端槽位 -> 回到任务详情 -> 执行 smoke flow”手工检查；若 UI 行为不一致，先补失败截图或 DOM 观察，再改实现。
- 证据位置：单元测试输出、手工检查清单、相关相对路径。
```

## 4. 收尾检查

- 每个未验证项是否写清“具体缺口 + 原因 + 下一步第一条动作”？
- 最终报告是否把“已验证事实”和“合理推断/未验证结论”分开？
- 验证失败是否改变了范围、顺序、目标或交接，而不是只改变措辞？
- 如果失败来自启动前 dirty path，是否明确未接管边界并避免全量提交？
- 如果失败来自环境依赖，是否记录了可重跑命令和需要的依赖，而不是只写“待验证”？

参考卡片：`books/tech-cards-handbook/chapters/ai-agent/verify-before-optimistic-summary.md`、`books/tech-cards-handbook/chapters/ai-agent/unverified-items-need-explicit-handoff.md`、`books/tech-cards-handbook/chapters/ai-agent/failure-output-must-change-plan.md`。
