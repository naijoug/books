# 技术卡片随身宝典

> 一本面向日常开发的短卡片手册。每张卡片只解决一个具体问题：什么时候用、怎么写、哪里容易错。

## 当前状态

本书已按技术栈重组正式内容：`chapters/` 下每个技术栈一个目录，每张卡片一个 Markdown 文件。

当前共 267 张正式卡片。

## 目录结构

```text
tech-cards-handbook/
├── README.md
├── chapters/
│   ├── README.md
│   ├── ai-agent/
│   ├── flutter/
│   ├── go/
│   ├── python/
│   ├── react/
│   ├── rust/
│   ├── swift/
│   └── typescript/
├── samples/
│   ├── README.md
│   ├── ai-agent-sample-pack.md
│   ├── ai-agent-dirty-workspace-one-pager.md
│   └── ...
├── .drafts/
└── resources/
```

正式卡片只放在 `chapters/<tech-stack>/` 下。可复制的 agent 输入、审查样例、一页纸模板和交接片段放入 `samples/`。草稿和未定稿片段放入 `.drafts/`，图片、图表、截图和参考素材放入 `resources/`。

## 正式内容

| 技术栈 | 目录 | 内容 |
|---|---|---|
| 索引 | `chapters/README.md` | 阅读方式、技术栈目录和维护规则 |
| Python | `chapters/python/` | 23 张：异步、并发、类型、测试与错误恢复 |
| Go | `chapters/go/` | 18 张：并发、接口、HTTP 边界与错误恢复 |
| Rust | `chapters/rust/` | 20 张：所有权、类型边界、异步、存储与错误恢复 |
| TypeScript | `chapters/typescript/` | 32 张：类型建模、DTO、状态分层与错误恢复 |
| React | `chapters/react/` | 54 张：状态、表单、异步数据、渲染与性能 |
| Swift | `chapters/swift/` | 14 张：值语义、异步、集合与错误恢复 |
| Flutter | `chapters/flutter/` | 14 张：布局、状态、生命周期与错误恢复 |
| AI Agent | `chapters/ai-agent/` | 92 张：运行控制、验证与证据、所有权与交付、产品化阶梯；按场景入口查找 |
| 样本索引 | `samples/README.md` | 可复制输入的场景入口：完整 dirty workspace 接力、短接力一页纸、失败吸收、proof 到 preflight 决策表、轻量 proof、全量 proof 基线、统一 preflight wrapper、命令梯、未验证项交接、验证失败交接、最终报告字段速查、AI 编程审查一页纸、案例发布阶梯、skill 复用判断、外部发布授权和 review note 发布门禁 |
| 样本包 | [场景索引](samples/README.md) | 先选择当前任务需要的一份输入；完整背景和案例按需展开 |

## 文件命名

卡片文件使用英文 `kebab-case` 命名，例如：

- `asyncio-reduces-waiting.md`
- `sync-waitgroup-goroutine-completion.md`
- `agent-model-tool-loop-boundaries.md`

不要使用 `01.md`、`02.md` 这类纯数字命名。阅读顺序由各技术栈目录下的 `README.md` 维护。

## 代码审查工具箱

当卡片不只是用来学习，而是要直接服务一次代码审查时，优先从这些清单入口开始：

| 审查主题 | 入口 | 适用场景 | 输出物 |
|---|---|---|---|
| 存储边界 | [`chapters/storage-boundary-review-checklist.md`](chapters/storage-boundary-review-checklist.md) | CRUD、后台管理、API handler、repository、ORM adapter | `输入 DTO / 领域 command/model / 存储 row / 输出 DTO` 字段映射表，以及不符合项记录 |
| 错误边界 | [`chapters/error-boundary-review-checklist.md`](chapters/error-boundary-review-checklist.md) | service、repository、handler、CLI command、外部 SDK adapter | `底层错误 / 领域错误 / 调用方动作 / 重试/降级策略 / 对外消息` 决策表，以及 P0–P3 优先级记录 |

使用方式：先用清单做 10–15 分钟快速走查，只记录“现象 + 风险 + 建议修复”；需要补背景时再跳到清单里的 Go / Rust 深度卡片。这样可以避免在 review 现场按语言特性发散，而是围绕边界是否泄漏、调用方能否稳定决策、对外契约是否安全来收束。

## 卡片标准

索引、样本或本地链接变更后运行 `python3 scripts/verify_tech_cards.py --full-only`，检查链接路径、卡片计数和样本索引。代码示例改动加跑 `python3 scripts/verify_all_cards.py --language <language>`；AI Agent 工作流卡片只做相关文档检查。verifier 自身改动再运行对应回归测试；完整的三组回归和三组书稿检查用 `python3 scripts/verify_tech_cards.py`，wrapper 自身改动还需 `python3 scripts/test_verify_tech_cards.py`。检查范围与格式要求见 [技术栈索引](chapters/README.md)。

每张正式卡片必须包含：

```text
问题：解决什么开发问题
要点：核心规则或判断标准
示例：最小代码或伪代码
坑：最容易写错的地方
检查：读者如何验证自己用对了
```

## 后续优先级

1. 优先补已有卡片的运行环境、可验证示例和交叉引用，按真实问题缺口决定新增内容。
2. AI Agent 目录优先统一边界判断和术语，避免为相同问题不断增加卡片或模板。
3. 发布前统一术语、难度标识和交叉引用；卡片数量由现有 verifier 校验。
