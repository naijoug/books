# 项目切片先闭环，再提取可复用资产

**问题**：AI 程序员在一个真实项目里刚完成一段小改动后，常常马上想把经验写成 `docs/`、`skills/` 或书稿卡片。怎样判断这次经验已经值得沉淀，并避免在项目尚未闭环时把“半成品观察”包装成资产？

**要点**：

- 先证明项目切片已经闭环：明确 touched paths、通过的验证命令、未验证边界和 commit / handoff 状态；否则只留下 notebook 接力，不急着抽象。
- 从重复判断里提取资产，而不是从单次实现细节里提取资产：例如“disabled command 要有本地反馈”比“某个按钮颜色改成灰色”更可复用。
- 资产形状按下一轮用途选择：要指导执行写 `skills/skills/...`，要解释方法写 `docs/...`，要进入长期书稿写 `books/...`，不要同一轮机械铺满三处。
- 新资产必须降低下一轮选择成本：它应该提供入口、停止条件、验证方式或模板；如果只是复述本轮做过什么，继续留在 `summaries/hermes/YYYY-MM-DD.md`。
- 提取后要反向链接到实际项目证据：记录相对路径、验证命令和相关文档，例如 `docs/documents/trending/ai/project-implementation-to-reusable-asset.md`，让读者能追溯它来自哪类真实闭环。

本卡负责判断“项目证据是否足以开始资产化”。如果已经有 docs / skill / book 两个互补表面，继续新增第三处前先回到 [`no-new-surface-without-reuse-proof.md`](no-new-surface-without-reuse-proof.md)，写出下一轮会如何复用它；否则停止扩表面，转为使用已有资产推进真实任务。

**示例**：

```text
项目切片：
- 在 skills/apps/packages/skills-ui/ 中完成 inline command rows：显式 > 触发、真实 command registry、disabled row feedback、DOM proof。
- 验证：UI test/typecheck 通过；只提交本轮 touched paths；skills/output/ 保持未接管。

资产提取判断：
- 重复判断："最小命令入口不要伪装成全局 overlay"、"enabled/disabled command 都要可验证反馈"。
- 下一轮用途：其它产品也可能需要把搜索框升级为轻量命令入口。
- 资产形状：先写一个 design skill，补 filled example、adoption checklist 和 decision snippet；再写一篇 docs 方法说明。
- 停止规则：如果下一轮只是想继续解释同一经验，就先复用已有 skill 或 docs，不再新增平行资产。
```

这样做的收益是：项目实现提供证据，skill 提供下一次执行入口，docs 解释抽象方法，书稿卡片压缩成长期判断规则；四者不互相替代，也不在同一层重复膨胀。

**坑**：

- **项目未绿先写资产**：测试失败、diff 范围不清或未提交状态没读回时，资产会把未验证假设固化。
- **把实现细节当资产**：记录某个 CSS 值、函数名或目录名，下一轮换项目就无法复用。
- **同一经验多处复制**：docs、skill、book 同时写同一段话，会增加维护成本；每一处都要说明自己的用途差异。
- **没有停止规则**：只说“后续继续沉淀”，会把心跳任务拖成无限内容扩张。
- **缺少反向证据**：不写验证命令、相对路径和 dirty 边界，读者无法判断这条卡片来自真实闭环还是事后想象。

**检查**：准备把项目经验写成资产前，先回答五个问题：项目切片是否已经有验证证据；可复用判断是否脱离具体实现名；选择 docs、skill、book 的理由是否不同；是否写清停止规则；下一轮能否只凭这张卡找到第一条安全动作。任一项答不上来，先回到项目或 notebook 补证据，不要急着新增资产。
