# Skill Metadata 是执行入口，不是装饰字段

**问题**：Agent 已经把技能正文写进 `SKILL.md`，为什么 linker、slash command、安装列表或搜索结果仍然让下一轮找不到、选不准或看见空标题？因为 `skill.yaml` 这类 metadata 不是文档装饰，而是执行入口的一部分。正文教人怎么做，metadata 决定工具能否发现、展示、触发和迁移这个技能。

**要点**：

- 把 metadata 当成“机器可读的门面”：至少包含稳定 `id`、可读 `title`、一句话 `summary`、分类 `tags`、触发关键词和兼容工具。
- 先保护用户可见入口，再追求完整 schema：空标题、缺摘要、无触发词会让好技能在列表中等同不可用。
- 补 metadata 时必须读正文，不要只把目录名 title-case；`summary` 要写“何时用 + 产出什么”，而不是复述文件名。
- 门禁应先轻量化：一个 dependency-free 脚本检查 `SKILL.md` 旁是否有 `skill.yaml`，再逐步扩展必填字段、重复 id、README 索引和 linker 输出。
- 失败要改变流程：如果聚合检查因为无关 typecheck 红灯失败，记录阻塞并先修 green baseline；不要把 metadata 清零说成全仓库健康。
- 资产化顺序要克制：先在源 repo 建门禁，再把经验沉淀到 docs 或书稿；不要在缺口还存在时只写方法论。

**示例**：

```text
Observation:
manual skill 目录下有多个 `SKILL.md`，但部分目录缺 `skill.yaml`；`skills-linker list --category manual` 能列出 id，却出现空标题或无法判断用途。

Human hypothesis before agent:
如果先补一个高价值技能的 metadata，再把“有 SKILL.md 但缺 skill.yaml”写成轻量检查，下一轮新增技能时会在提交前发现可发现性退化。

Change:
- 为 `skills/manual/review/path-scoped-commit-boundary/skill.yaml` 补 `id/title/summary/tags/triggers/compatibility`。
- 在 README 目录树暴露该技能。
- 新增 `apps/scripts/check-skill-metadata.py`，默认扫描 manual skill 并在缺 metadata 时失败。
- 把脚本接入 `apps/scripts/skills-manager-check`。

Verification ladder:
1. `python3 apps/scripts/check-skill-metadata.py`
2. `python3 apps/scripts/check-skill-metadata.py --category all`
3. `./apps/skills-manager-tui/skills-linker list --category manual | grep <skill-id>`
4. 用临时 fixture 构造“只有 SKILL.md、没有 skill.yaml”的负例，确认脚本非零退出。
5. `apps/scripts/skills-manager-check`

Handoff:
本轮修的是技能可发现性和检查入口，不改变技能正文语义；若下一轮继续扩字段校验，先加正反向 fixture，再修改脚本。
```

**坑**：

- **把 metadata 当发布后补充**：正文合并后再想起补 `title` 和 `summary`，linker 已经可能把空入口暴露给用户。
- **只检查文件存在**：有 `skill.yaml` 但 `title: ""`、`summary: ""` 或 `triggers.keywords: []`，仍然会让搜索和选择退化。
- **批量猜测摘要**：一次生成几十个 summary，容易把适用场景写偏；更安全的是按高价值路径一项一提交。
- **门禁太重**：metadata 检查依赖完整前端构建或包安装，会失去 fail-fast 价值；轻量检查应该能在最小环境里先跑。
- **索引不同步**：只让 linker 可见，不更新 README 或目录入口，下一轮人工接力仍会找不到。
- **把检查红灯包装成成果**：如果统一检查里有既有 typecheck 红灯，报告必须写清“metadata 检查已过，但聚合检查被某项阻塞”。

**检查**：提交前逐条确认：新增或修改的技能是否有稳定 `id`、清晰 `title`、可判断适用场景的 `summary`、非空触发关键词和兼容工具；README 或索引是否能从人工入口到达该技能；linker 输出是否显示正确标题；metadata 检查是否有正反向验证；最终 notebook 是否写清本轮只拥有的路径和未接管 dirty path。任一项缺失，就不要把这次改动称为“技能已可复用”。
