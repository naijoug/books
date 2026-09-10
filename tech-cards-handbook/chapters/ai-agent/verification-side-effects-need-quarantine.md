# 验证副作用要隔离，不要让 proof 命令顺手改出提交内容

## 问题

Agent 在无人值守任务里经常会运行 `check`、`build`、`generate` 或 `test` 命令来证明本轮改动可用。但很多验证命令并不只读：它们可能刷新 API contract、格式化快照、重写 generated 文件、留下临时数据库，或者更新缓存。若收尾时只看“命令通过”，就容易把验证副作用当成本轮成果提交，或在恢复副作用时误删真正需要刷新的产物。

验证命令不是天然可信边界。它执行之后必须有一次 post-snapshot，把差异分成“本轮必需变化”“验证副作用”“未知 dirty”，再决定 stage、恢复或交接。

## 要点

- **验证前先有 baseline。** 在运行可能写文件的命令前，记录目标 repo 的 `git status --short`；如果已有 dirty path，默认不接管。
- **验证后立刻做 post-snapshot。** 命令返回 0 之后马上再读 `git status --short`，不要等到提交前才发现多了 generated diff。
- **把差异分三类。** `required` 是本轮目标需要提交的文件；`generated-side-effect` 是验证命令刷新但不属于本轮目标的文件；`unknown` 是启动前已有或无法解释的文件。
- **恢复要 path-specific。** 只对确认是验证副作用的 path 执行 `git restore -- <path>` 或删除临时目录；不要用 `git reset --hard`、`git clean -fd` 这种会伤到别人改动的命令。
- **如果生成物本应更新，改走 artifact 漂移流程。** 需要提交 tracked generated artifact 时，写清生成命令、漂移原因和提交范围；否则按验证副作用隔离。
- **notebook 写清副作用处理。** 交接里要说明哪些 path 是验证命令产生、已恢复或未接管，避免下一轮误以为它们是业务改动。

## 示例

一个低风险的验证后隔离流程：

```bash
# 1. 验证前快照
before="$(mktemp)"
git status --short > "$before"

# 2. 运行可能产生 generated diff 的验证命令
pnpm check

# 3. 验证后快照
after="$(mktemp)"
git status --short > "$after"
diff -u "$before" "$after" || true

# 4. 只恢复已确认的验证副作用
# 例：pnpm check 重新生成 contract，但本轮只改 README
git restore -- backend/src/contracts/spec.ts frontend/shared/src/contracts/generated.ts

# 5. stage 前再次确认只剩本轮路径
git status --short
git add -- README.md docs/requirements.md
git diff --cached --name-status
```

在 notebook 里不要只写“`pnpm check` passed”，而要补上副作用分类：

```text
验证副作用：`pnpm check` 生成 `backend/src/contracts/spec.ts` 和 `frontend/shared/src/contracts/generated.ts` diff；本轮目标是文档引用修正，生成物不属于 required diff，已用 path-specific restore 恢复。
提交前 index：只包含 `README.md`、`docs/requirements.md`。
未接管：启动前已有 curriculum dirty path，保持排除。
```

如果验证命令通过但新增了不在 owned paths 里的文件，把 scope proof 记录到可复查的字段里，而不是用一句“已清理”带过：

```text
Owned paths before verification:
- chapters/ai-agent/verification-side-effects-need-quarantine.md

Pre-check status:
- clean

Verification command:
- python3 scripts/verify_tech_cards.py --full-only

Post-check new dirty paths:
- chapters/api/generated-contract.md

Classification:
- chapters/api/generated-contract.md => generated-side-effect, outside owned paths

Action:
- git restore -- chapters/api/generated-contract.md
- git add chapters/ai-agent/verification-side-effects-need-quarantine.md
- git diff --cached --name-only

Decision:
- Continue, because staged paths are still limited to owned paths.
```

## 坑

- **把 green check 当作 clean repo。** 测试通过只说明断言通过，不说明工作区仍干净。
- **用全局恢复命令清理副作用。** `git reset --hard` 和 `git clean -fd` 在 dirty workspace 里可能删除用户或其他 agent 的改动。
- **把 generated diff 一律恢复。** 有些生成物是 tracked artifact 的契约部分；若本轮改了 schema、打包脚本或内容源，应先证明它需要刷新，而不是机械丢弃。
- **提交前没有读 cached diff。** `git status` 只能说明工作区有什么，不能证明本次 commit 只包含本轮 owned paths。
- **只在最终报告里说“已清理”。** 下一轮需要知道副作用来自哪条命令、哪些 path 被恢复、哪些 path 仍然排除。

## 检查

收尾前确认：

1. 是否在运行验证命令前后都保存了 `git status --short`？
2. 验证后新增或变化的 path 是否已分类为 `required`、`generated-side-effect` 或 `unknown`？
3. 对副作用的恢复是否只针对明确 path，而不是全仓库清理？
4. 如果 generated artifact 被提交，是否有漂移检查或生成命令说明支撑？
5. `git diff --cached --name-status` 是否只包含本轮 owned paths？
6. notebook 和最终报告是否写清验证副作用、恢复动作、未接管边界和下一步接力？
