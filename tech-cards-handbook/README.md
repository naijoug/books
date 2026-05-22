# 技术卡片随身宝典

> 一本面向日常开发的短卡片手册。每张卡片只解决一个具体问题：什么时候用、怎么写、哪里容易错。

## 当前状态

本书已按技术栈重组正式内容：`chapters/` 下每个技术栈一个目录，每张卡片一个 Markdown 文件。

当前共 97 张正式卡片。

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
├── .drafts/
└── resources/
```

正式卡片只放在 `chapters/<tech-stack>/` 下。草稿和未定稿片段放入 `.drafts/`，图片、图表、截图和参考素材放入 `resources/`。

## 正式内容

| 技术栈 | 目录 | 内容 |
|---|---|---|
| 索引 | `chapters/README.md` | 阅读方式、技术栈目录和维护规则 |
| Python | `chapters/python/` | 18 张：异步、并发原语、上下文管理、生成器、类型、测试和装饰器 |
| Go | `chapters/go/` | 10 张：WaitGroup、context、channel、worker pool、select、mutex、错误处理、接口和测试 |
| Rust | `chapters/rust/` | 12 张：所有权、借用、Option、Result、trait、生命周期、模式匹配、模块、迭代器、并发、异步和测试 |
| TypeScript | `chapters/typescript/` | 9 张：联合类型、条件类型、`infer`、Mapped Type、深度只读、`satisfies`、`unknown` 和模板字面量类型 |
| React | `chapters/react/` | 10 张：Effect、状态、表单、列表 key、ref、自定义 Hook、错误边界、回调身份和性能 |
| Swift | `chapters/swift/` | 9 张：值语义、async/await、基础值、字符串、集合、switch、可选绑定、闭包和 defer 清理 |
| Flutter | `chapters/flutter/` | 10 张：状态、列表、导航、测试、布局、输入控件、组件拆分、异步构建、生命周期检查和 controller 释放 |
| AI Agent | `chapters/ai-agent/` | 19 张：Agent 边界、工具、工具结果、记忆、反馈判断、反馈修订、反馈池、迭代上限、心跳工作流、交接、接力取舍、短节拍边界、验证总结、未验证项交接、提交状态读回、失败输出吸收和助手操作系统 |

## 文件命名

卡片文件使用英文 `kebab-case` 命名，例如：

- `asyncio-reduces-waiting.md`
- `sync-waitgroup-goroutine-completion.md`
- `agent-model-tool-loop-boundaries.md`

不要使用 `01.md`、`02.md` 这类纯数字命名。阅读顺序由各技术栈目录下的 `README.md` 维护。

## 卡片标准

每张正式卡片必须包含：

```text
问题：解决什么开发问题
要点：核心规则或判断标准
示例：最小代码或伪代码
坑：最容易写错的地方
检查：读者如何验证自己用对了
```

## 后续优先级

1. 将 TypeScript、React、Swift 和 Flutter 目录继续扩展到接近 Python 的密度。
2. AI Agent 目录已超过 Python 当前密度，后续优先补运行示例、交叉引用和术语统一，而不是机械增卡。
3. 为每个代码片段补充可运行环境或最小测试。
4. 新增卡片时继续按“问题、要点、示例、坑、检查”的格式写。
5. 发布前统一术语、难度标识和交叉引用。
