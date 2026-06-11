# 技术卡片随身宝典

> 一本面向日常开发的短卡片手册。每张卡片只解决一个具体问题：什么时候用、怎么写、哪里容易错。

## 当前状态

本书已按技术栈重组正式内容：`chapters/` 下每个技术栈一个目录，每张卡片一个 Markdown 文件。

当前共 177 张正式卡片。

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
| Python | `chapters/python/` | 22 张：异步、并发原语、上下文管理、生成器、类型、测试、装饰器、自定义异常层级、显式重试策略、领域定义的对外错误码和调用方降级策略 |
| Go | `chapters/go/` | 17 张：WaitGroup、context、channel、worker pool、select、mutex、错误处理、接口、测试、HTTP handler adapter 边界、跨语言错误传播对照、显式重试策略、领域定义的对外错误码和调用方降级策略 |
| Rust | `chapters/rust/` | 19 张：所有权、借用、Option、Result、trait、生命周期、模式匹配、模块、迭代器、并发、异步、测试、newtype 领域边界、From/TryFrom 验证边界、repository 存储边界、derive 语义选择、显式重试策略、领域定义的对外错误码和调用方降级策略 |
| TypeScript | `chapters/typescript/` | 26 张：联合类型、`never` 穷尽检查、条件类型、`infer`、Mapped Type、深度只读、`satisfies`、`unknown`、类型守卫、断言函数、外部 schema 边界、请求状态分层、品牌类型、模板字面量类型、Result 错误处理、工具类型、DTO 边界、DTO 版本演进、DTO 字段迁移、消费者观测、事件分层、mapper 边界、ViewModel 边界和 Command 边界 |
| React | `chapters/react/` | 54 张：Effect、状态、派生状态、URL 状态、服务端数据缓存、异步状态边界、请求过期保护、请求缓存去重、缓存 key 设计、缓存失效、缓存过期、搜索防抖、骨架屏、表单字段状态、提交状态、字段错误、幂等键、action 返回 contract、成功后重置、列表 key、虚拟列表、分页加载、加载更多并发锁、筛选排序重置、延迟渲染、过渡更新、ref、自定义 Hook、错误边界、Suspense、代码分割、可恢复重试、Context 拆分、回调身份、memo、Profiler、性能、乐观更新、React 19 表单状态、SSR hydration 稳定输入、浏览器 API 客户端读取、客户端个性化外壳、SSR 个性化首屏占位策略、外部 store、Strict Mode、Reducer 和状态机 |
| Swift | `chapters/swift/` | 10 张：值语义、async/await、基础值、字符串、集合、switch、可选绑定、闭包、defer 清理和 Result 错误状态 |
| Flutter | `chapters/flutter/` | 10 张：状态、列表、导航、测试、布局、输入控件、组件拆分、异步构建、生命周期检查和 controller 释放 |
| AI Agent | `chapters/ai-agent/` | 21 张：Agent 边界、工具、工具结果、记忆、上下文预算、上下文状态设计、反馈判断、反馈修订、反馈池、迭代上限、心跳工作流、交接、接力取舍、短节拍边界、验证总结、未验证项交接、提交状态读回、失败输出吸收、启动层边界和助手操作系统 |

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
