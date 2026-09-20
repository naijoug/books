# 本地书稿写作工具

显式调用 Claude CLI，按目标书定位完成写作或审查。平时直接编辑书稿不需要经过本工具。共享提示词和脚本纳入 Git；本目录其余本地文件仍被忽略。

## 按任务选择

| 任务 | 入口 | 结果 |
|---|---|---|
| 新写内容 | `write` + [写作规则](writer_agent.md) | Markdown 正文；指定目标时只写入 `.drafts/` |
| 审查 | `review` + [审查规则](editor_agent.md) | 报告返回终端；只有 `--output` 才保存 |
| 按意见修订 | `rewrite` | 默认生成同一本书 `.drafts/` 中的 `_v2.md`；`--apply` 明确写回原稿 |
| 写作并修订 | `full` | 生成候选稿、审查、修订、再次审查；末轮问题在终端返回 |
| 核验事实 | `search` 或 `--research` + [检索规则](search_prompt.md) | 来源、日期、证据与尚未核验的部分 |

小修不强制研究或双角色审查；长章节和技术卡片各自遵守目标书的结构。`full` 只处理指定草稿，不自动发布或承诺出版就绪。

## 使用

从仓库根目录运行，需要已配置的 `claude` CLI。命令会调用模型；本地回归测试不调用模型。

```bash
python3 .agents/book_writer.py write '解释 Agent 的工具边界' ai-agent-best-practices/.drafts/tool-boundaries.md
python3 .agents/book_writer.py review ai-agent-best-practices/chapters/07-tool-integration.md
python3 .agents/book_writer.py rewrite ai-agent-best-practices/chapters/07-tool-integration.md
python3 .agents/book_writer.py rewrite ai-agent-best-practices/chapters/07-tool-integration.md --apply
python3 .agents/book_writer.py full '解释 Agent 的工具边界' ai-agent-best-practices/.drafts/tool-boundaries-new.md --research
python3 .agents/book_writer.py search '本次书稿中需要核验的具体 API 与版本'
```

`review --output /tmp/chapter-review.md` 可显式保存审查报告，后续作为 `rewrite <章节> <报告>` 的输入。不传报告时，rewrite 会先进行一次审查。现有目标文件不会被候选稿或报告覆盖；`--apply` 写回前检查原稿是否在生成期间发生变化。

模型仅使用读取工具；启用研究时增加 WebSearch / WebFetch。脚本限制内置工具，关闭技能和隐式 MCP 配置，由 Python 保存返回正文；继承的 CLI/组织策略仍适用。JSON 结果必须成功且正文非空；超时、非零退出、错误结果不会作为本次书稿保存，stderr 仅显示在终端。full 中途失败时保留此前已成功写入的草稿，不把部分结果报告为全流程完成。

来源是否足以支撑结论仍需审查。CLI 成功、引用格式通过和代码运行通过是不同证据；不得互相替代。

## 本地检查

```bash
python3 scripts/test_book_writer.py
```

测试使用临时目录和模拟 CLI 响应，覆盖审查不落盘、候选稿路由、错误退出、保留已有文件及修订反馈流。
