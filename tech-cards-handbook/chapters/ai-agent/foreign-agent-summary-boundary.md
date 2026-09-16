# 其他 Agent Summary 边界先于提交范围

## 问题

多 Agent workspace 里，`summaries/` 往往同时承载 Hermes、OpenClaw 或未来更多 agent 的工作记录。周期性唤醒的 Agent 做启动快照时，可能看到其他 agent 目录里有未跟踪或未提交文件。它们同处一个 git repo，很容易被 `git add .` 或“顺手整理 summary”的动作混进当前 Agent 的提交。

共享 summary 仓库里的未跟踪文件不是当前 Agent 的默认工作范围。看见它们，只能证明需要边界记录；不能证明可以代写、改写、提交或清理。

## 要点

- **先区分 repo 归属与目录归属。** `summaries/` 是共享 repo，但 `summaries/hermes/`、`summaries/openclaw/` 等目录仍有 agent 归属边界。
- **其他 agent summary 默认只读观察。** 可以在自己的 notebook 里记录它存在、未接管和未提交，但不要打开后修格式、补标题或代写内容。
- **提交范围必须 path-scoped。** 提交 Hermes notebook 时只 stage `hermes/YYYY-MM-DD.md`；提交前用 `git diff --cached --name-only` 确认 staged list 只包含自己的 notebook path，没有混入其他 agent 目录。
- **把 staged list 当允许列表，不当提醒列表。** 只要 `git diff --cached --name-only` 出现 `openclaw/...`、其他 agent 目录或任何非本轮 notebook path，就先 unstage，再重跑检查；不要靠 commit message 或最终报告“解释掉”混入的 path。
- **不要把未跟踪当垃圾。** 其他 agent 的 `?? openclaw/YYYY-MM-DD.md` 可能是刚生成但还没提交的 notebook，不是可以删除的临时文件。
- **边界要写进接力记录。** 如果其他 agent path 连续多轮出现，下一轮需要知道这是“刻意未接管”，不是漏处理。
- **只有明确授权才跨目录维护。** 用户要求迁移、合并或修复其他 agent summary 时，才把目标 path 纳入本轮 owned scope，并在 commit message 中写清跨 agent 维护范围。

## 示例

启动快照显示：

```text
summaries:
?? openclaw/2026-09-14.md
?? openclaw/2026-09-15.md
```

不要为了让 `summaries/` clean 就执行 `git add .`。先把分诊写成当前 Agent 的边界记录：

```text
Startup signal:
- summaries repo has untracked files under summaries/openclaw/.

Ownership decision:
- Hermes does not own openclaw summary files in this run.
- Treat them as foreign-agent summary paths: read-only observation, no edit, no commit.

Owned paths for this run:
- summaries/hermes/2026-09-15.md

Pre-commit guard:
- git add hermes/2026-09-15.md
- git diff --cached --name-only
- expected staged list contains only hermes/2026-09-15.md
```

提交前命令梯保持最小范围：

```bash
cd summaries

git status --short

git add hermes/2026-09-15.md

git diff --cached --name-only

git diff --cached --check

git commit -m "docs: update hermes notebook for 2026-09-15"
```

如果 `git diff --cached --name-only` 出现 `openclaw/`，先取消暂存：

```bash
git restore --staged openclaw/2026-09-15.md
```

## 坑

- **用 `git add .` 省事。** 在共享 summary repo 中，这会把其他 agent 的 notebook 和当前 Agent 的记录混进同一个 commit。
- **把“同一个 repo”误读成“同一个 owner”。** repo 级权限不等于任务级所有权；目录归属仍然要独立判断。
- **顺手统一格式。** 给其他 agent summary 补标题、改用词或重排段落，看似无害，实际会破坏对方记录的原始状态。
- **最终报告只报自己的 commit，不报排除边界。** 用户和下一轮 Agent 会误以为 remaining untracked path 是本轮遗漏。
- **复制对方 summary 当成果。** Hermes notebook 可以记录“看到并避开”，不能把其他 agent 的内容包装成本轮推进。

## 检查

收尾前确认：

1. `summaries/` 中其他 agent 目录的 dirty path 是否已经被标注为 foreign-agent summary，而不是 owned path？
2. 本轮是否只修改自己的 notebook 或明确授权的 summary maintenance 文件？
3. `git diff --cached --name-only` 是否只包含本轮 owned paths，且提交 Hermes notebook 时是否只包含 `hermes/YYYY-MM-DD.md`？
4. 如果 staged list 出现 `openclaw/...` 或其他非本轮 notebook path，是否已经 unstage 并重跑检查？
5. Hermes notebook 是否写清“未接管、不改写、不提交”的边界？
6. 最终报告是否列出未接管的其他 agent summary path，避免用户误解为遗漏？
7. 若确实跨 agent 维护，是否有用户授权、启动快照和 commit message 说明？
