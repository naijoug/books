# AI Agent 本地 proof checker 一页纸

用于文档、配置、索引或小型脚本改动：先用一个窄范围、可重复、能失败的本地检查证明“基础契约没有破”，再把主题渲染、插件行为、端到端集成交给重型构建。

## 1. 先定义本轮风险，不要先写万能 linter

```text
改动范围：<本轮明确接管的相对路径>
最容易破的契约：<链接/目录索引/frontmatter/include/绝对路径/生成物边界>
轻量 proof：<能在本地快速运行且失败时有明确输出的命令>
重型验证：<build/test/e2e，只验证轻量 proof 不覆盖的集成层>
```

例子：

```text
改动范围：documents/trending/ai/README.md 和 documents/trending/ai/checker.md。
最容易破的契约：跨目录相对链接指向不存在的脚本；文档里混入本机用户目录绝对路径。
轻量 proof：python3 scripts/check-markdown-proof.py <changed files>。
重型验证：VuePress build 只负责侧边栏、插件和页面渲染。
```

## 2. 最小检查边界

| 风险 | proof checker 适合做 | 留给重型构建或人工复核 |
|---|---|---|
| 本轮文件不存在或匹配 0 个文件 | 直接失败，避免假绿灯 | 无 |
| 本地相对链接、目录 README 省略后缀 | 检查是否能解析到真实文件 | 页面渲染后的导航体验 |
| VuePress `@include` 文件目标 | 检查 include 文件是否存在 | include 后的锚点、插件扩展语义 |
| frontmatter 必填字段 | 检查 `title` 等基础字段 | 主题如何展示 frontmatter |
| 绝对路径泄漏 | 检查本机用户目录等不可移植路径 | 内容语义是否仍合适 |
| 锚点、sidebar、搜索索引 | 通常不做，除非已有真实漏报样例 | build、预览或专门集成测试 |

## 3. 执行顺序

```text
1. 改前 proof：对将要修改的文件运行 checker，确认基线为绿。
2. 修改文件：只改本轮明确接管的路径。
3. 改后 proof：对同一组文件重跑 checker。
4. 失败处理：
   - 如果是本轮改动破坏契约，先修改动。
   - 如果是 checker 误报/漏报，先补最小 fixture，再改 checker。
5. 集成验证：需要时再运行 build/test，并写清它证明的是集成层。
6. 记录：notebook 同时写 proof checker、重型验证、未覆盖边界和下一轮第一条动作。
```

## 4. 可复制 notebook 句式

```text
- 实际推进：本轮围绕 <改动目标> 做 path-limited 修改；改前先运行 <proof command> 确认基线，通过后再改文件。
- 验证方式：改前 <proof command> 输出 <摘要>；改后同一命令输出 <摘要>；随后运行 <build/test command> 验证 <集成层边界>。
- 失败吸收：若 proof checker 报 <失败摘要>，本轮将 <修本轮改动/补最小 fixture/缩小范围>，不把失败包装成通过。
- 后续接力：下一次若出现 <真实误报/漏报条件>，先补 <最小 fixture 路径>；否则继续把 checker 当 preflight，不扩成万能 linter。
```

## 5. 收尾检查

- checker 是否在改前和改后都跑过，而不是只在最后跑一次？
- checker 是否会在目标不存在、匹配 0 个文件、链接只指向目录时失败？
- 每条新增规则是否来自真实误报/漏报或最小 fixture？
- 最终报告是否区分“轻量 proof 覆盖的基础契约”和“重型构建覆盖的集成层”？
- 文档和 notebook 是否只使用相对路径，避免把当前机器路径写成证据？
