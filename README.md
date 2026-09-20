# Books 写作仓库

每本书独立维护 Markdown 书稿。当前进度和下一步以各书 README 为准，仓库目录约束见 [AGENTS.md](AGENTS.md)。

## 书籍入口

| 书名 | 读者与主题 |
|---|---|
| [《AI 时代个人提升指南》](ai-personal-growth/README.md) | 普通知识工作者、学生、创作者和程序员；学习、工作、创作与职业成长 |
| [《AI Agent 最佳实践指南》](ai-agent-best-practices/README.md) | 开发者和技术负责人；Agent 架构、工具、评估、部署与安全 |
| [《技术卡片随身宝典》](tech-cards-handbook/README.md) | 日常开发；按语言和工程问题查找短卡片 |

## 按任务选择资料

- 新增或重组内容：查看目标书的定位和目录；候选内容先进入 `.drafts/`，进入正式书稿结构后放入 `chapters/`。
- 局部修订：读取目标段落和直接相关引用；涉及目录或计数时同步对应索引。
- 事实更新：核验变化的 API、版本、数据或结论，保留来源和真实访问日期。
- 发布整理：按该书检查清单复核结构、术语、引用和格式。
- 使用本地写作 CLI：查看 [.agents/README.md](.agents/README.md)。它是显式调用的写作工具，不是每次编辑的前置流程。

审查发现默认在对话中汇报；README 只维护当前状态和剩余工作，历史修改可通过 Git 查询。

## 验证入口

命令从仓库根目录运行。选择与改动有关的检查，失败后修复本轮引入的问题再重跑相关检查。

| 改动 | 检查 |
|---|---|
| 普通文案 | 审读修改段落，运行 `git diff --check -- <paths>` |
| 技术卡片目录、计数、样本或本地链接 | `python3 scripts/verify_tech_cards.py --full-only` |
| 技术卡片中的语言代码示例 | 加跑 `python3 scripts/verify_all_cards.py --language <language>` |
| 个人成长书的外部引用 | `python3 scripts/verify_ai_personal_growth_refs.py` |
| 卡片 verifier 实现 | 对应 `scripts/test_verify_*.py`；聚合回归与书稿检查用 `python3 scripts/verify_tech_cards.py` |
| 引用日期校验或写作 CLI | 分别运行 `python3 scripts/test_verify_ai_personal_growth_refs.py`、`python3 scripts/test_book_writer.py` |

卡片检查覆盖本地链接路径、卡片计数和样本索引；不验证外链可达性或锚点。个人成长书检查引用格式与日期合法性，不证明来源内容仍然正确。写作 CLI 测试使用临时书稿和模拟进程，不调用付费模型。
