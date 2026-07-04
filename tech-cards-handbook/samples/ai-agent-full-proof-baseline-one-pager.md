# AI Agent 全量 proof 基线一页纸

用于已经有轻量 proof checker 的仓库：先把全量命令跑成可解释的红绿基线，再决定它是否能进入 `AGENTS.md`、preflight wrapper 或 CI。它不替代 changed-file proof，而是回答“仓库级基线是否已经可信”。

## 1. 先写升级候选，不要先写规则

```text
候选命令：<全量 proof 命令，例如 python3 scripts/check-markdown-proof.py documents>
升级位置：<AGENTS.md / scripts/preflight / CI / 只保留为手动命令>
当前用途：<一次性基线扫描 / checker 回归 / 大范围结构改动前后>
常规小改用途：<changed-file proof 命令>
不覆盖边界：<渲染/sidebar/插件/端到端行为/人工语义审查>
```

如果还不能填出“不覆盖边界”和“常规小改用途”，先不要把全量命令写成必跑项。

## 2. 红灯分类表

| 失败类型 | 判断标准 | 本轮动作 | 升级前要求 |
|---|---|---|---|
| 真实内容破损 | 链接、include、frontmatter、路径等基础契约确实坏了 | 修内容，并记录受影响路径 | 改后同一全量命令通过 |
| checker 误报 | 内容按仓库约定有效，但 checker 解析错 | 补最小 fixture 或回归测试，再修 checker | regression + 全量 proof 都通过 |
| checker 漏报 | 人工发现基础契约坏了但 checker 没报 | 先补最小失败样本，再补规则 | 新规则不会误伤现有有效写法 |
| 集成边界 | 需要主题、插件、构建或浏览器才能判断 | 不塞进轻量 proof；交给 build/e2e/人工预览 | 文档写清不覆盖项和触发条件 |
| 旧问题暂不接管 | 启动前已存在，超出本轮范围 | notebook 写清未接管边界和下一条安全命令 | 不把红灯命令升级为必跑项 |

## 3. 执行顺序

```text
1. 启动快照：记录目标 repo 的 git status，确认本轮只接管哪些 path。
2. 改前全量 proof：运行候选命令，保存失败摘要。
3. 分类失败：逐项放入“真实内容 / checker / 集成边界 / 未接管旧问题”。
4. 修最小闭环：只修本轮明确接管的内容或 checker 规则；误报必须有最小回归证据。
5. 改后验证：运行 checker regression、changed-file proof、全量 proof；需要时再跑 build。
6. 升级判断：只有全量 proof 变绿，且失败语义可解释，才写入 AGENTS、preflight wrapper 或 CI 候选。
7. 交接：写清全量 proof 与 changed-file proof 的分工，以及下次失败时先看哪份证据。
```

## 4. 可复制 notebook 句式

```text
- 实际推进：本轮围绕 <目标> 先建立 full proof baseline；改前 <full command> 输出 <失败/通过摘要>，失败项按 <分类> 处理。
- 验证方式：<regression command> 输出 <摘要>；<changed-file proof command> 输出 <摘要>；<full proof command> 输出 <摘要>。这些只覆盖 <基础契约>，不覆盖 <集成边界>。
- 升级判断：当前 <可以/不可以> 写入 <AGENTS/preflight/CI>；理由是 <全量绿基线/仍有未接管旧问题/仍有误报/缺少回归测试>。
- 后续接力：下一次若 <full command> 失败，先按红灯分类表判断是本轮改动、旧问题、checker 误报还是集成边界，不要直接把失败包装成通过。
```

## 5. 收尾检查

- 全量命令是否真的在改前和改后跑过，而不是只把 changed-file proof 结果当作全量基线？
- 每个失败项是否有分类和路径证据？
- checker 修复是否有最小 regression，而不是靠人工相信？
- 全量 proof 通过后，是否仍保留 changed-file proof 作为日常小改入口？
- 如果全量 proof 仍红，是否明确写成“暂不升级”，而不是塞进常规 preflight？
- notebook 和最终报告是否只使用相对路径？
