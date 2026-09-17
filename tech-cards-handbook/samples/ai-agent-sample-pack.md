# AI Agent 工作流卡片 · 样本包

> 本样本包不是 AI Agent 章节的完整目录，而是一条可复制的 dirty workspace 心跳接力主线：10 张精选卡片负责建立最小闭环，附录和配套模板负责把它落到真实 prompt、验证证据和最终报告字段。
> 选自《技术卡片随身宝典》AI Agent 系列（共 92 张）。如果只想减少一次无人值守接力的事故率，先按本包顺序走完；如果要扩展到运行控制、验证与证据、所有权与交付、产品化阶梯四条主线，再回到完整章节目录。
> 第一次使用时，先读 `books/tech-cards-handbook/chapters/ai-agent/README.md` 的“本章四条主线”和“3 分钟读法”，再复制本样本包；这样能先分清本包主要覆盖运行控制与验证证据，哪些所有权、交付和产品化判断要回到完整章节或样本索引补齐，避免把样本当成机械待办。
> 阅读顺序就是这条链路的决策顺序：心跳/日志资产化/快照 → 规划 → 接力信号 → 无人值守默认动作 → 失败吸收 → 归属边界 → 状态证据 → 验证与报告；样本卡片只保留最小闭环，完整 quick path 和一页纸入口见文末参考卡片与配套模板。
> 如果你的目标不只是让接力更稳，而是把一次 AI 编程审查转成收入实验，先用本包稳住 dirty workspace，再在文末“收入实验接力”里复制审查报告一页纸和案例发布阶梯；不要把未验证的交付物直接包装成公开战报。

## 验证入口速记

只想决定下一份验证输入时，先用这张“验证入口速记”表，从“当前最大风险”做一次入口判断，不要在 proof、baseline、wrapper 和命令梯之间反复切换：

| 当前最大风险 | 复制哪份输入 | 通过后下一步 |
|---|---|---|
| 小改动需要证明基础契约，但全量构建太重 | [`ai-agent-proof-checker-one-pager.md`](ai-agent-proof-checker-one-pager.md) | 若 proof 连续稳定，再考虑全量基线 |
| 想把 checker 写进 AGENTS、preflight 或 CI，但还不知道全量是否真的绿 | [`ai-agent-full-proof-baseline-one-pager.md`](ai-agent-full-proof-baseline-one-pager.md) | 先分类失败项；只有稳定绿项进入常规必跑 |
| 验证命令超过三条，下一轮容易漏跑或报告漂移 | [`ai-agent-preflight-wrapper-one-pager.md`](ai-agent-preflight-wrapper-one-pager.md) | 给 wrapper 补默认/快速模式和编排测试 |
| 不确定该选 proof、baseline、wrapper、命令梯还是交接模板 | [`ai-agent-proof-to-preflight-decision-table.md`](ai-agent-proof-to-preflight-decision-table.md) | 按矩阵选一个入口，不要同时复制多份 |
| 已经知道最大风险，只缺下一条安全命令和停止条件 | [`ai-agent-next-safe-command-ladder-one-pager.md`](ai-agent-next-safe-command-ladder-one-pager.md) | 把验证结果写回 notebook 和最终报告 |
| crawler、parser、adapter 链路缺测试，但最直接入口需要 protected/private mock | `books/tech-cards-handbook/chapters/ai-agent/parser-layer-test-ladder-before-protected-mocks.md` | 先按 config/factory/scheduler/parser utility/controller 找低 mock 层；仍不能覆盖风险时再进入 protected parser |
| 薄 API/controller/middleware 已有 integration 200，但短路、校验、404/409 或错误转发没被锁住 | `books/tech-cards-handbook/chapters/ai-agent/thin-api-tests-target-control-flow-not-200.md` | 先补控制流与下游不调用断言；如果只剩 200 happy path 就停止 |
| 评估报告、发布报告和安全门禁之间字段名开始漂移 | [`ai-agent-evidence-field-handoff-one-pager.md`](ai-agent-evidence-field-handoff-one-pager.md) | 先填字段生产者/补齐者/消费者表，再区分“字段名一致”和“真实流水线已跑通” |
| 本轮产物是 zip、静态页、清单或模板包，担心页面锚点、staging 残留、归档契约或 tracked artifact 漂移 | 先读 `books/tech-cards-handbook/chapters/ai-agent/README.md` 的“交付工程化线索” | 把交付检查拆成页面结构、临时输出、归档内容和已追踪生成物四层 |
| `summaries/`、共享 notebook 或多 agent 仓库里出现其他 agent 的未跟踪记录，担心误 stage 或替对方提交 | `books/tech-cards-handbook/chapters/ai-agent/foreign-agent-summary-boundary.md` | 把它标成 `foreign-summary`：只读观察、写入本轮未接管边界，不进入本轮 stage 列表 |

判断口径：先问“我要降低哪一个风险”，再选模板；不要因为模板已经存在就机械补齐。若当前风险是命令失败或未覆盖边界，优先使用失败吸收、验证失败交接或未验证项交接模板，而不是继续升级 preflight；若当前风险是跨 agent notebook 或共享 summary 仓库污染，先收紧提交范围，而不是继续补验证命令。

---

## 卡片 1：心跳工作流让长期任务不漂移

**问题**：长任务运行一段时间后，如何避免忘记目标、只产出噪音或停在半路？

**要点**：

- 心跳不是激励语，而是状态闭环。
- 最小流程是：读取状态 → 生成提醒 → 执行自检 → 写回进展。
- 每次心跳都要留下下一轮能读取的证据。

**示例**：

```text
心跳检查：{task_name}
上次状态：{last_progress}
请用 3 行更新：
1. 已完成：
2. 阻碍：
3. 下一步：
```

**坑**：只发送"继续努力"这类提醒，很快会变成噪音；没有写回动作，就不能形成系统。

**检查**：下一次运行能否从心跳记录里直接知道当前阻碍和下一步？能，才算闭环。

---

## 卡片 2：工作日志是可复用资产，不要写成心情流水账

**问题**：心跳型 Agent 每轮都会写 notebook、summary 或交接记录，如何避免这些记录只变成“我做了什么”的流水账，而是成为下一轮可直接复用的资产？

**要点**：

- 日志要服务接力，不是服务存在感；每段记录必须能回答“当前状态、候选工作、取舍理由、实际推进、验证证据、下一条动作”。
- 把事实、推断和计划分开写：事实来自命令、diff、文件路径或测试输出；推断要说明依据；计划要落到下一条可执行动作。
- 记录要能反向审计提交范围：变更文件、验证命令、commit hash、未接管边界必须能对上实际 repo 状态。

**示例**：

```text
上一段/当前状态：books clean；loom 启动前已有 dirty path，未接管。
本轮选择：修改 books/.../samples/...，因为它是 clean repo 的低风险文档小块。
验证证据：git diff --check；python3 scripts/verify_tech_cards.py --full-only。
后续接力：下一轮先检查 samples/README.md 是否需要同步入口文案。
```

**坑**：只写“继续优化”“已完成总结”，却不写为什么没碰 dirty repo、验证命令是什么、下一轮第一条命令在哪里；下一轮只能重新摸索，日志没有变成资产。

**检查**：另一个 Agent 只读这段日志，能否在不猜测的情况下复现本轮提交边界、验证证据和下一步？能，才算可复用资产。

---

## 卡片 3：启动快照先于规划，不要凭上一轮印象选任务

**问题**：心跳型 Agent 醒来后，如何避免把上一轮 `Next path` 误当成当前可安全执行的命令？

**要点**：

- 规划前先记录当前时间、workspace root、候选 repo 的 `git status --short`。
- 上一轮交接只是输入，不是义务；如果接力 path 启动前已经 dirty，先降级为归属判断。
- dirty path 至少标注 `known-own`、`previous-agent`、`user-or-unknown`、`generated/noise`。

**坑**：只读 notebook，不跑当前 git 状态；上一轮记录的是过去状态，不代表现在仍然安全。

**检查**：规划里的选择理由，能否从启动快照推出？如果不能，先补快照再选任务。

---

## 卡片 4：规划要选择工作，不要只复述状态

**问题**：周期性运行的 Agent 如何避免把“复盘”和“总结”误当成本轮成果？

**要点**：

- 规划必须列出候选项、选择项、放弃项和选择理由。
- 选择要落到低风险、可验证的小块，而不是停在宏观方向。
- 如果只能观察，也要把观察转成下一轮第一条可执行动作。

**坑**：写“继续推进 AI 能力建设”“后续完善项目”这类愿望句，没有排除项、风险判断和第一条命令。

**检查**：另一个 Agent 读完规划后，能否在 1 分钟内判断本轮为什么做这件事、哪些事故意没做、下一步从哪里开始？

---

## 卡片 5：接力点是信号，不是义务

**问题**：上一轮 Agent 已经写了“后续接力”，下一轮是否必须照做？

**要点**：

- 接力点是优先检查的信号，不是自动执行的命令；新一轮仍要重新评估风险、收益和验证成本。
- 先问三件事：这件事是否仍然有价值？能否缩成一个低风险小块？本轮能否验证完成？
- 如果答案不满足，最多尝试缩小一次；仍然过大，就明确切换到更小、更可验证的工作，并在记录中写清切换理由。

**示例**：

```text
上一轮接力：给日志过滤增加 next/prev 跳转。
本轮评估：需要当前匹配索引、DOM refs、滚动定位和键盘语义，验证成本超过本轮节拍。
决策：暂停 UI 跳转，改为沉淀接力点取舍规则。
后续接力：若之后有完整 UI 时间，再从滚动定位设计开始。
```

**坑**：把交接当成待办队列，机械执行，导致小任务逐步膨胀；或只写“本轮不做”，但不说明价值、风险和验证成本。

**检查**：记录里能否同时看到“为什么优先看这个接力点”和“为什么本轮执行或放弃它”？如果只剩结论，没有取舍过程，就还没有真正完成接力判断。

---

## 卡片 6：无人值守 Agent 要选择默认动作，不要等待澄清

**问题**：cron、scheduled job 或 CI 里的 Agent 没有用户在场，遇到轻微歧义时应该怎么办？

**要点**：

- 先判断歧义是否真的会改变下一条工具调用；不会改变时，采用最安全、最小范围的默认解释继续推进。
- 默认动作要同时满足三点：低风险、可验证、可回滚；例如只读检查、path-limited 文档改动、聚焦测试。
- 如果歧义涉及外部副作用、账号权限、删除数据或跨 repo 大改，停止在只读阶段，并把需要用户决策的问题写成下一段接力。
- 最终记录要写出本轮采用的默认解释，而不是假装用户已经确认。

**示例**：

```text
输入：检查“当前项目”还有什么值得推进。
环境：workspace 根目录不是 git repo，多个子 repo dirty，用户不在线。
默认解释：先检查各子 repo 状态；不接管启动前 dirty path；选择 clean repo 中一个独立、可验证的小文档任务。
验证：只对本轮文件跑 git diff --check 和结构断言；提交后读回 hash。
```

**坑**：把“不能问问题”理解成可以猜测用户授权，或因为不能确认就完全不行动、只留下空泛计划。

**检查**：无人值守记录里能否看到“默认解释是什么、为什么低风险、验证证据在哪里、哪些问题留给用户决策”？看不到，就还不是可接力的自治动作。

---

## 卡片 7：失败输出要改变计划，不要当作背景噪音

**问题**：Agent 已经看到命令失败、工作区 dirty、测试不通过或搜索结果缺失时，如何避免继续按原计划推进，最后把失败信号包装成顺利完成？

**要点**：

- 失败输出不是“记录一下就算了”，它必须改变至少一项：范围、顺序、目标或交接。
- 先判断失败类型：环境失败、前置条件失败、验证失败、边界失败、信息缺口；不同类型对应不同调整。
- 如果失败来自非本轮改动或边界不清，优先缩小范围或切换到干净 repo，不要用全量命令继续制造噪音。
- 最终报告要写出“失败输出如何改变了本轮计划”，而不只是写“遇到失败但已处理”。

**示例**：

```text
原计划：继续修改 loom 的日志面板。
工具输出：git status 显示 loom 已有多处非本轮 UI/设计文件改动。
计划调整：不碰 loom；切换到干净的 books 写一张独立卡片；最终报告说明 loom dirty 是目标切换原因。
```

```text
失败吸收速记：
- 范围缩小：全量测试失败且落在启动前 dirty 模块 -> 本轮只提交当前文档，把代码测试失败列为未接管边界。
- 顺序变更：diff --check 失败 -> 先修格式并重跑，再做结构断言和提交。
- 目标切换：候选 repo 启动前 staged/unknown -> 改选 clean 项目 repo，并在 notebook 写明切换原因。
- 交接改写：依赖缺失导致验证无法执行 -> 最终报告写未验证项，后续接力给出下一条命令和依赖。
```

如果本轮失败信号较多，先用 [`ai-agent-failure-absorption-one-pager.md`](ai-agent-failure-absorption-one-pager.md) 把每条失败写成“信号 -> 影响 -> 证据位置”，再决定它改变范围、顺序、目标还是交接。

当失败已经阻断验证，不要只把它塞进最终报告的一句话；改用 [`ai-agent-verification-failure-handoff-template.md`](ai-agent-verification-failure-handoff-template.md) 拆出一个最小交接块：

```text
已验证：<仍然可信的命令或人工检查>
未验证：<被失败阻断的范围 + 失败归属>
结论措辞：<本轮只能说什么，不能说什么>
下一步：<按失败归属选择的第一条动作>
证据位置：<命令输出、diff、notebook 段落或相对路径>
```

**坑**：测试失败后只改最终措辞，不改变验证策略或实现方案；搜索或读取没有结果时继续凭记忆写结论。

**检查**：每条关键失败输出都能在计划、执行记录或后续交接中看到对应变化；如果看不到范围、顺序、目标或交接的改变，说明 Agent 只是观察到了失败，还没有吸收失败。

---

## 卡片 8：未提交接力文件先判断归属，不要直接接管

**问题**：上一轮记录的接力点正好对应 repo 里的未提交文件，下一轮 Agent 能不能直接继续改、一起提交？

**要点**：

- 未提交文件可能来自用户、另一个 Agent、失败生成物或上一轮未提交产物，不是天然可接管工作区。
- 只有 `known-own` 可以直接 stage；`previous-agent` 也要先重新验证，再 path-limited staging。
- `user-or-unknown` 不要为了完成接力而改写或提交；应记录未接管边界，换一个 clean 小任务。
- `foreign-summary`（例如共享 `summaries/` repo 里其他 agent 的 notebook）只能只读观察、写入排除边界；不能代写、改写、提交或清理。
- 最终报告必须保留状态证据：启动快照、收尾 `git status --short`、项目 repo 与 `summaries` repo 各自的 commit hash。

**坑**：看到上一轮写“继续 Day 3”，又看到同名 dirty 文件，就直接 `git add docs/` 提交。

**检查**：最终报告里出现某个未提交文件时，能否回答它在本轮开始时是否已存在、本轮改了哪一行、提交时是否只 stage 本轮路径、收尾状态证据是否支持“未接管边界”？答不出就不要纳入成果。

---

## 卡片 9：提交范围台账防止混入未知归属

**问题**：多个子 repo 同时 dirty 时，Agent 如何防止把启动前已有、归属未知或其他 agent 的改动一起提交？

**要点**：

- 在 stage 前维护一张最小台账：`repo / path / 启动状态 / 本轮动作 / 是否提交 / 验证证据 / 状态证据`。
- 每个准备提交的 path 都必须能回答“本轮改了什么、验证在哪里、为什么可以 stage”。
- 台账里的 `不提交` 不是失败，而是边界证据；最终报告要保留这些排除项，方便下一轮继续判断。
- 启动快照、提交前 index 快照、收尾 status 是三类不同证据：分别证明“起点边界”“stage 范围”和“最终状态”。

**示例**：

```text
repo       path                                      启动状态          本轮动作        是否提交  验证证据                  状态证据
books      tech-cards-handbook/samples/...          clean             新增样本段落    是        diff --check + 关键词断言  启动/收尾 status clean
docs       documents/awesome/ai/agent.md            dirty/unknown     只读观察        否        启动快照                  收尾仍 dirty，未 stage
summaries  openclaw/2026-09-15.md                   foreign-summary   只读观察        否        启动快照                  收尾仍未跟踪，未 stage
loom       docs/PLANS.md                            staged/unknown    未接管          否        启动快照 + index 快照      收尾仍 staged/unknown
```

**坑**：只在脑中记得“我没碰那些文件”，但 stage 时使用 `git add .` 或 `git add docs/`；最终报告只写本轮 commit，不写被排除的 dirty path。

**检查**：提交前的 `git diff --cached --name-status` 是否只包含台账中 `是否提交=是` 的 path？最终报告是否能从台账直接复制完成项、启动/收尾状态证据和未接管边界？

---

## 卡片 10：最终报告要写清排除边界，不要只报完成项

**问题**：Agent 正确只提交了自己的文件，为什么最终报告仍可能误导下一轮或用户？

**要点**：

- 最终报告不只列“做了什么”，还要列“哪些已有改动没有接管”。
- 排除边界必须来自本轮启动或收尾的 `git status --short`，并使用相对路径。
- 如果某个候选任务因为 dirty 状态被放弃，最终报告要把它放到“未接管/下一段接力点”。
- 收尾顺序固定为：验证证据 → 状态证据 → 已提交状态读回 → 排除边界；没有项目提交或 notebook 提交也要写 `未提交`，不要删除字段。

**坑**：只写 commit hash，不写未接管边界；下一轮可能误把旧脏文件当成本轮成果提交。

**检查**：最终报告至少能回答四件事：本轮提交了哪个 repo 的哪些成果；启动/收尾 `git status --short` 证据是什么；notebook 记录在哪里；哪些启动前已有或未归属的相对路径明确没有接管。

---

## 附录：错误边界 review agent 输入样例

这份样本包主线是 Agent 工作流卡片；如果要把它用于真实代码审查，可以从一个足够小的错误边界任务开始。下面这个输入样例的目标不是让 Agent 一次性审完整个系统，而是把范围压到一条可验证调用链，并强制它留下证据、决策表和失败出口。

```text
请使用 skills/skills/manual/review/error-boundary/ 审查以下模块的错误边界。

语言栈：TypeScript
待审范围：services/profile/http.ts、services/profile/client.ts、services/profile/errors.ts
对外接口：GET /api/profile/:id
关键调用链：profileHttpHandler -> getProfileForResponse -> profileClient.fetchProfile
已知错误类型：ProfileMissing、ProfileUnavailable、第三方 SDK timeout；其他未知
允许的恢复动作：ProfileMissing 可 degrade；ProfileUnavailable 可 retry 2 次后 return public error；未知错误 escalate
公开响应约束：允许 code/message/degraded；禁止暴露 host、path、SDK 原始 message、token、SQL 或内部 trace id
需要重点检查：底层错误是否翻译成领域错误；调用方是否显式决定 retry/degrade；公开响应是否脱敏；cause/inner 是否保留

输出要求：
1. 先给出“底层错误 / 领域错误 / 调用方动作 / 重试或降级策略 / 对外 code-message / 证据路径”的决策表。
2. 再按 P0–P3 列出 findings；每条包含证据、风险、修复建议和建议测试。
3. 如果缺少 diff hunk、函数名、公开响应契约或失败测试，先输出 NARROW_FIRST，不要编造 PR 评论。
4. 最后写一段交接记录：使用清单 books/tech-cards-handbook/chapters/error-boundary-review-checklist.md，使用 skill skills/skills/manual/review/error-boundary/，下一位 reviewer 优先检查哪一列。
```

**检查**：如果 Agent 的输出没有相对路径证据、没有决策表，或者把“看日志确认”当作测试，这次 review 还没有闭环；先要求它回到 `NARROW_FIRST`，补齐缺失证据后再升级到 findings 或 patch。

---

## 附录：dirty workspace 心跳交接输入样例

当 Agent 被周期性唤醒、workspace 里已经有多个 repo 处于 dirty 状态时，不要把“继续上次接力点”当作自动义务。先用下面的输入样例约束它完成启动快照、归属判断、path-limited 推进和最终报告边界。如果只需要一页纸版本，使用 `samples/ai-agent-dirty-workspace-one-pager.md`；如果上一轮点名的目标文件已经在启动快照里 dirty，先按 `chapters/ai-agent/dirty-target-file-blocks-continuation.md` 记录 `blocked continuation`、排除 path 和回归条件，再切到 clean replacement，不要因为它是接力点就顺手修。

一页纸里已经包含一个最小记录示例和最终报告模板，覆盖 `git -C books diff --check`、Python 结构断言、`git -C books add --`、`git -C books commit -m`、`rev-parse --short HEAD`、本轮变更文件、启动/收尾 status 证据和启动前 dirty path 的未接管说明。把本附录作为完整 prompt 使用时，建议在执行要求里保留同样的证据链：先验证、再 path-limited stage、记录状态证据、提交后读回 hash、最后按“验证证据 -> 状态证据 -> 已提交状态读回 -> 排除边界”报告未接管边界。

```text
你正在一个已有 dirty workspace 的长期任务里工作。

启动前必须先记录：
1. workspace 根目录是否是 git repo；
2. 每个相关 repo 的 git status --short；
3. 上一轮 notebook 写下的 Next path / Next slice；
4. 哪些 dirty path 在本轮启动前已经存在。

决策规则：
- 接力点只是信号，不是义务；如果接力文件启动前已 dirty，先判断归属。
- 如果上一轮明确点名的目标文件启动前已 dirty，默认降级为 `blocked continuation`：只读 intake、记录排除 path 和回归条件，然后选择 clean replacement；除非有明确证据证明这是自己本轮可接管的 known-own 改动，否则不 stage、不顺手修。
- 如果处在 cron、scheduled job、CI 等无人值守环境，不能等待澄清时，要先写出默认解释，再选择低风险、可验证、可回滚的小动作。
- 如果上一轮验证、测试或命令输出失败，先判断它是否改变本轮范围、顺序、目标或交接；不要一边沿用原计划，一边把失败写成背景噪音。
- 只有 known-own 或有明确证据可接管的 previous-agent 文件才能 stage。
- user-or-unknown、generated/noise、无法解释来源的 dirty path 一律不 stage，只记录未接管边界。
- 共享 `summaries/` repo 中其他 agent 目录（例如 `summaries/openclaw/...`）默认标成 `foreign-summary`：只读观察，写入未接管边界，不代写、不清理、不提交。
- 如果项目 repo 不适合动，选择一个 clean repo 的独立小任务推进。

执行要求：
1. 先写“上一段/当前状态、候选工作、本轮选择、选择理由、下一段计划”。
2. 修改文件前检查项目 repo 状态；修改后只对本轮文件做 diff --check 和结构断言。
3. 验证失败时必须回到规划：说明失败改变了什么、缩小了什么，或为什么只作为未验证项交接；如果不知道怎么写交接块，复制 `books/tech-cards-handbook/samples/ai-agent-verification-failure-handoff-template.md`。
4. 提交时只使用 path-limited staging，不使用 git add .；提交 notebook 前用 `git diff --cached --name-only` 确认只包含自己的 summary path（例如 `summaries/hermes/YYYY-MM-DD.md`）。
5. 最终报告必须使用标准字段名 `项目提交`、`notebook 提交`，同时列出启动/收尾 `git status --short` 证据，以及未接管 dirty path 的相对路径和原因。
6. 最终报告固定字段都要保留；没有发生的项目写 `无` 或 `未提交`，不要删掉字段让下一轮猜测。

最终报告可复制模板：

收尾顺序固定为：`验证证据 -> 状态证据 -> 已提交状态读回 -> 排除边界`。不要只写“验证通过”；要写命令、结果摘要、仍未验证的部分，以及启动/收尾 `git status --short` 摘要。commit 信息从提交后的状态读回，至少包含 hash 和 subject，避免把计划中的提交误报成已经落地。

字段顺序固定为：`本轮选择 -> 实际推进 -> 变更文件 -> 验证证据 -> 状态证据 -> 写入 notebook -> 项目提交 -> notebook 提交 -> 未接管边界 -> 下一段接力`。如果某一项没有发生，也保留字段并写“无”或“未提交”，不要删除字段让下一轮猜测。

提交读回的最短写法：

```text
项目提交：books `19bbcfa` `Link AI agent sample pack to reading path`（提交后用 `git -C books log -1 --oneline` 读回）。
notebook 提交：summaries `8c026a9` `Record Hermes heartbeat progress`（提交后用 `git -C summaries log -1 --oneline` 读回）。
未提交：项目 repo 本轮无可提交改动；仍保留字段，不把计划中的提交写成已落地。
```

- 本轮选择：{选择的 repo / 文件 / 小任务}，原因：{为什么它比其他候选更安全或更有价值}。
- 实际推进：{具体改动 1–3 条}。
- 变更文件：{本轮实际修改或提交的相对路径；无则写“无”}。
- 验证证据：{命令及结果摘要，例如 diff --check、结构断言、测试命令；未验证项也要写明}。
- 状态证据：{启动和收尾 git status --short 摘要；说明本轮外 dirty path 是否仍未接管}。
- 写入 notebook：summaries/hermes/YYYY-MM-DD.md。
- 项目提交：{repo} `{short_hash}` `{subject}`（如有；从已提交状态读回）。
- notebook 提交：`summaries` `{short_hash}` `{subject}`（如有；从已提交状态读回）。
- 未接管边界：{repo/path + 原因，例如启动前已 dirty、归属未知、非本轮文件}。
- 下一段接力：{下一轮优先打开的相对路径、第一条动作和 verification destination}。

未接管边界的正反例：
- ✅ `未接管边界：无（启动和收尾 status 均未发现本轮外 dirty path）。`
- ✅ `未接管边界：docs/documents/awesome/ai/agent.md 启动前已 dirty，归属未知，未 stage。`
- ❌ 省略 `未接管边界` 字段。

参考卡片（按 `心跳/日志资产化/快照 -> 规划 -> 接力信号 -> 无人值守默认动作 -> 失败吸收 -> 归属/验证/报告` 的 quick path 顺序排列；完整路径见 `books/tech-cards-handbook/chapters/ai-agent/README.md` 和 `books/tech-cards-handbook/samples/ai-agent-dirty-workspace-one-pager.md`）：
- books/tech-cards-handbook/chapters/ai-agent/heartbeat-workflow-prevents-drift.md
- books/tech-cards-handbook/chapters/ai-agent/work-log-is-reusable-asset.md
- books/tech-cards-handbook/chapters/ai-agent/startup-snapshot-before-planning.md
- books/tech-cards-handbook/chapters/ai-agent/planning-selects-work-not-just-summary.md
- books/tech-cards-handbook/chapters/ai-agent/continuation-is-signal-not-obligation.md
- books/tech-cards-handbook/chapters/ai-agent/dirty-target-file-blocks-continuation.md
- books/tech-cards-handbook/chapters/ai-agent/unattended-agent-chooses-default-action.md
- books/tech-cards-handbook/chapters/ai-agent/failure-output-must-change-plan.md
- books/tech-cards-handbook/chapters/ai-agent/uncommitted-handoff-needs-ownership-triage.md
- books/tech-cards-handbook/chapters/ai-agent/staged-changes-are-not-ownership.md
- books/tech-cards-handbook/chapters/ai-agent/commit-scope-ledger-prevents-mixed-ownership.md
- books/tech-cards-handbook/chapters/ai-agent/dirty-workspace-exit-checklist.md
- books/tech-cards-handbook/chapters/ai-agent/verify-before-optimistic-summary.md
- books/tech-cards-handbook/chapters/ai-agent/parser-layer-test-ladder-before-protected-mocks.md
- books/tech-cards-handbook/chapters/ai-agent/unverified-items-need-explicit-handoff.md
- books/tech-cards-handbook/chapters/ai-agent/local-proof-checker-precedes-heavy-build.md
- books/tech-cards-handbook/chapters/ai-agent/full-proof-baseline-before-ci.md
- books/tech-cards-handbook/chapters/ai-agent/unified-preflight-wrapper-prevents-command-drift.md
- books/tech-cards-handbook/chapters/ai-agent/report-from-committed-state.md
- books/tech-cards-handbook/chapters/ai-agent/final-report-names-excluded-boundaries.md

交付工程化补充卡片（当本轮成果会被下载、发布或复用时再接入，不要替代上面的 dirty workspace 边界）：
- books/tech-cards-handbook/chapters/ai-agent/referenced-section-needs-stable-anchor.md
- books/tech-cards-handbook/chapters/ai-agent/package-staging-stays-outside-output-dir.md
- books/tech-cards-handbook/chapters/ai-agent/artifact-smoke-test-checks-contract.md
- books/tech-cards-handbook/chapters/ai-agent/tracked-artifact-needs-drift-check.md
- books/tech-cards-handbook/chapters/ai-agent/shared-package-assertions-prevent-contract-drift.md

接入顺序：前四张先证明单个交付物的锚点、staging、归档契约和 tracked artifact 漂移；只有当同类 package smoke test 已在两个以上交付物中重复出现时，才接入共享断言卡，避免为了“抽象”牺牲每个包自己的交付语义。

配套模板：
- books/tech-cards-handbook/samples/ai-agent-final-report-field-quickref.md
- books/tech-cards-handbook/samples/ai-agent-proof-to-preflight-decision-table.md
- books/tech-cards-handbook/samples/ai-agent-proof-checker-one-pager.md
- books/tech-cards-handbook/samples/ai-agent-full-proof-baseline-one-pager.md
- books/tech-cards-handbook/samples/ai-agent-preflight-wrapper-one-pager.md
- books/tech-cards-handbook/samples/ai-agent-next-safe-command-ladder-one-pager.md
- books/tech-cards-handbook/samples/ai-agent-unverified-handoff-one-pager.md
- books/tech-cards-handbook/samples/ai-agent-verification-failure-handoff-template.md
```

**检查**：如果最终输出只列完成项、不列未接管边界，或者 notebook 里没有说明为什么避开某个 dirty repo，这次心跳仍不具备可接力性；下一轮应该先回到归属判断，而不是继续提交。

---

## 附录：收入实验接力输入样例

当 dirty workspace 心跳已经跑通，下一步可以把一次小范围 AI 编程审查变成可交付的收入实验。不要跳过固定范围、证据边界和发布降级：交付给客户的是审查报告，不是“AI 全自动改好一切”；公开复盘前先判断材料能否支撑 claim。

```text
你正在把一次 AI 编程审查做成固定范围收入实验。

启动前必须先确认：
1. 待审范围是否能在 30–60 分钟内读完；
2. 输入证据是否包含 diff、关键调用链、运行命令或失败输出；
3. 哪些信息只能写成 Fact / Inference / Unverified；
4. 是否有客户、项目或公开 repo 的授权边界。

执行顺序：
1. 先读 `books/tech-cards-handbook/chapters/ai-agent/ai-coding-audit-is-fixed-scope-offer.md`，把服务压成一个固定范围 offer。
2. 用 `books/tech-cards-handbook/samples/ai-agent-audit-report-one-pager.md` 填交付报告：Scope、Executive Summary、Top Risks、Next Safe Command Ladder、Handoff Template、Continue / Narrow / Stop。
3. 如果材料不足以支持风险结论，先降级为 `NARROW_FIRST` 或 `Unverified`，不要补想象中的测试结果。
4. 如果想把交付物转成内容或案例，再用 `books/tech-cards-handbook/samples/ai-agent-case-publishing-ladder-one-pager.md` 判断 Evidence shape、公开边界和 Claim labels。
5. 如果内容准备外发到社媒、邮件列表、群组或付费渠道，先填 `books/tech-cards-handbook/samples/ai-agent-external-publish-authorization-one-pager.md`；缺少明确 offer / 实验、渠道授权、账号/身份、回复入口、目标对象或受众、观察窗口时，默认结论是 `Wait for authorization`，不是继续润色文案。
6. 公开输出只能使用可公开证据；客户私有上下文、未验证推断和缺失命令必须降级或删除。

最终报告固定字段：
- Offer scope：<本次审查包含/不包含什么>
- Evidence used：<相对路径、diff、命令输出或公开链接>
- Top risks：<最多 3 条，带 Fact / Inference / Unverified 标签>
- Next safe command：<下一条最小验证命令或需要补的证据>
- Delivery artifact：books/tech-cards-handbook/samples/ai-agent-audit-report-one-pager.md
- Publishing decision：<Continue / Narrow / Stop + 原因>
- Case artifact：books/tech-cards-handbook/samples/ai-agent-case-publishing-ladder-one-pager.md
```

参考卡片：
- books/tech-cards-handbook/chapters/ai-agent/ai-coding-audit-is-fixed-scope-offer.md
- books/tech-cards-handbook/chapters/ai-agent/first-report-before-consulting.md
- books/tech-cards-handbook/chapters/ai-agent/thirty-minute-route-before-productizing.md
- books/tech-cards-handbook/chapters/ai-agent/ai-assisted-pr-review-path-is-product-ladder.md
- books/tech-cards-handbook/chapters/ai-agent/publish-feedback-needs-evidence-shape.md
- books/tech-cards-handbook/chapters/ai-agent/anonymous-case-must-not-invent-evidence.md
- books/tech-cards-handbook/chapters/ai-agent/public-case-separates-facts-inferences-unverified.md

配套模板：
- books/tech-cards-handbook/samples/ai-agent-audit-report-one-pager.md
- books/tech-cards-handbook/samples/ai-agent-case-publishing-ladder-one-pager.md
- books/tech-cards-handbook/samples/ai-agent-external-publish-authorization-one-pager.md

**检查**：如果报告里没有明确 Scope、证据路径、未验证项和下一条安全命令，就不能称为可交付审查；如果公开复盘没有 Evidence shape 和 Claim labels，或外部发布没有授权包，就只能保留为内部复盘或方法样板。

---

## 附录：技能化判断输入样例

当一次心跳或审查里出现“这条观察好像可以沉淀成新 skill”的冲动时，先不要直接新建技能目录。先用 skill 复用一页纸判断它是单次任务、已有 skill 的补充引用，还是确实达到新 skill 门槛；只有能证明跨场景复用、触发条件清晰、已有 skill 无法覆盖，才进入技能化。

```text
你正在判断一次 AI 编程观察是否值得沉淀成新 skill。

启动前必须先确认：
1. 观察来自哪次任务、哪个相对路径、哪条验证证据；
2. 是否已有 skill、卡片、docs 或样本能覆盖同类问题；
3. 这条观察是否已经在两个以上场景复现，还是只是一次 Narrow 结果；
4. 如果不新建 skill，下一轮 Agent 是否仍能通过现有入口复用它。

执行顺序：
1. 先读 `books/tech-cards-handbook/chapters/ai-agent/reuse-existing-skill-before-new-skill.md`。
2. 填写 `books/tech-cards-handbook/samples/ai-agent-skill-reuse-before-new-skill-one-pager.md` 的观察快照、复用路径、停止条件和技能化门槛。
3. 若已有 skill 只缺触发例子，优先补 reference 或 notebook 接力，不新建 skill。
4. 若证据不足，把结论写成 `Reuse / Watch / New skill candidate`，并留下下一次复核的第一条命令或文件。

最终报告固定字段：
- Observation source：<相对路径、命令输出或任务记录>
- Existing reuse path：<已有 skill/docs/books/samples 入口；没有则写无>
- Decision：<Reuse / Watch / New skill candidate>
- Stop condition：<为什么本轮不新建 skill，或触发新建的最低证据>
- Next review：<下一段第一条动作>
```

参考卡片：
- books/tech-cards-handbook/chapters/ai-agent/reuse-existing-skill-before-new-skill.md
- books/tech-cards-handbook/chapters/ai-agent/no-new-surface-without-reuse-proof.md
- books/tech-cards-handbook/chapters/ai-agent/work-log-is-reusable-asset.md

配套模板：
- books/tech-cards-handbook/samples/ai-agent-skill-reuse-before-new-skill-one-pager.md

**检查**：如果只能说“以后可能有用”，但没有观察来源、复用路径和停止条件，本轮应保持 `Watch`；不要把一次未复现的经验直接包装成新 skill。

---

## 关于完整版

这 10 张精选卡片选自《技术卡片随身宝典》AI Agent 系列的 92 张卡片。

完整版覆盖：工具契约与证据、上下文预算与状态设计、反馈闭环、运行控制、无人值守默认动作、交接机制、dirty workspace 收尾、失败输出改计划、交付工程化检查、最终报告边界和助手操作系统分层等主题。

每张卡片遵循统一格式：**问题 → 要点 → 示例 → 坑 → 检查**，适合在日常工作中随手翻阅、团队分享或作为 Agent 配对编程的参考。
