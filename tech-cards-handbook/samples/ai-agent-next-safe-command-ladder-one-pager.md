# AI Agent 下一条安全命令梯一页纸

> 配套卡片：`books/tech-cards-handbook/chapters/ai-agent/next-safe-command-ladder-is-not-test-list.md`。
> 用途：在心跳型 Agent、代码审查、文档发布或工具脚本改动中，把“验证清单”改写成下一条最能改变判断的命令梯。

## 1. 先写当前最大风险

不要从工具名开始写。先用一句话说明本轮最容易出错、且最值得先证明的风险。

```text
变更范围：<本轮 touched paths 或功能边界>
当前最大风险：<最可能让本轮结论失真的风险>
为什么不是先跑全量：<全量命令成本/噪声/定位能力不足的原因>
停止条件：<遇到什么就不继续扩大验证范围>
```

常见风险示例：

| 场景 | 当前最大风险 | 第一条命令倾向 |
|---|---|---|
| Markdown/目录入口改动 | 链接、frontmatter、include 目标坏了 | path-limited markdown proof 或链接扫描 |
| 小脚本改动 | 语法或核心 fixture 失效 | `py_compile` + 脚本自测 fixture |
| dirty workspace 中接力 | 混入启动前未知归属改动 | `git status --short` + path-limited diff |
| UI 小改 | 选择器或布局破坏关键路径 | 最小 smoke/visual fixture，而非全量 E2E |
| 构建配置改动 | 配置 schema 或入口文件错误 | 配置 parser/build dry-run |

## 2. 把清单改成命令梯

每一级都必须回答 `Pass means`、`Fail means` 和 `Escalate when`。如果答不上，就不要把它写进梯子。

```text
Command ladder:
1. <最便宜、最能定位当前最大风险的命令>
   - Pass means: <这一层证明了什么>
   - Fail means: <失败后缩小到哪里；是否停止>
   - Escalate when: <什么时候进入下一层>

2. <覆盖集成边界但仍相对聚焦的命令>
   - Pass means: <新增可相信的范围>
   - Fail means: <如何判断是本轮问题还是既有噪声>
   - Escalate when: <什么时候需要重型构建/CI/人工检查>

3. <重型构建、CI 或人工验收>
   - Pass means: <只能声明的集成结论>
   - Fail means: <记录真实错误；不要把未验证项包装成完成>
   - Stop when: <外部权限、未知 dirty path、依赖缺失或非本轮失败>
```

## 3. 可复制示例

```text
变更范围：books/tech-cards-handbook/samples 新增一页纸，并更新 AI Agent 章节入口。
当前最大风险：新增相对链接或样本入口写错，导致读者从 README 找不到模板。
为什么不是先跑全量：本轮没有代码执行路径；全量 verifier 只能证明索引计数，不能定位新增链接语义。
停止条件：如果 books 启动前出现非本轮 dirty path，不把它们一起 stage。

Command ladder:
1. python3 scripts/verify_tech_cards_index.py
   - Pass means: 章节卡片计数和索引仍一致。
   - Fail means: 先修 README/chapters index，不继续提交。
   - Escalate when: 新增或删除正式卡片，而不是只改 samples。

2. python3 <inline link scan over tech-cards-handbook/**/*.md>
   - Pass means: 新增样本和入口里的相对 markdown 链接能解析到文件。
   - Fail means: Narrow 到缺失 path 或错误相对层级。
   - Escalate when: 链接依赖 VuePress alias、插件或生成文件。

3. git diff --check -- <本轮 touched files>
   - Pass means: 本轮文件无空白/冲突标记等基础 diff 风险。
   - Fail means: 修本轮文件并重跑 1-3，不提交。
   - Stop when: diff 中出现启动前未知归属文件。
```

## 4. Notebook 句式

```text
验证方式：先按“当前最大风险 -> 下一条安全命令梯”排序验证，而不是直接列测试清单。
- 第 1 级：`<command>`，证明 `<pass means>`；失败时 `<fail means>`。
- 第 2 级：`<command>`，证明 `<pass means>`；失败时 `<fail means>`。
- 重型验证：`<command or not run>`；执行/未执行理由：`<reason>`。
- 未验证项：`<明确列出，不写成已完成>`。
```

## 5. 收尾检查

- 第一条命令是否直接对应当前最大风险？
- 每一级是否写清了 `Pass means` 与 `Fail means`？
- 失败后是否会改变范围、顺序、目标或交接？
- 重型构建/CI 是否只在需要证明集成边界时出现？
- 最终报告是否区分“已证明”“未验证”“未接管边界”？
