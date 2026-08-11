# 发布闸门先字段化，不要让 `--push` 读取散文结论

## 问题

Agent 在准备日报、资料包、落地页或 beta 分发时，常会先写一份发布复核记录。记录里可能已经有真实 URL、联系入口、人工复核、授权来源、remote、工作区状态等信息，但如果这些信息只散落在段落里，发布脚本很容易只看见“rehearsal passed”“检查完成”“看起来可以发”，然后把 `--push` 当成安全动作。

这张卡解决的问题是：如何把外部发布前的人工判断拆成机器可解析字段，让自动脚本只能在明确字段全部为 `Go` 时继续，而不是从散文、占位符或 dry-run 成功里推断授权。需要直接复制给下一轮 agent 或发布 reviewer 时，用 [`../../samples/ai-agent-publish-gate-review-note-one-pager.md`](../../samples/ai-agent-publish-gate-review-note-one-pager.md) 填 canonical review note、checker 输出和未触发副作用边界。

## 要点

1. **字段先于发布脚本**：在给 `publish`、`deploy`、`send`、`post` 增加真实副作用前，先定义发布复核记录的字段名、合法取值和默认值。
2. **证据和确认分两层**：脚本可以自动检查 URL 不是占位符、remote 存在、工作区是否干净，但只能给出 `Review` / `Wait` / `No-Go`；`Go` 必须来自人工确认字段或人工编辑后的复核记录。
3. **最终决策单独字段化**：`No-push rehearsal result: Pass`、`all checks passed`、`remote found` 都不能替代 `Final decision: Publish`。
4. **发布脚本显式读取复核文件**：`--push` 必须要求人工传入 `--review-note docs/...md`，不要自动选择“最新复核记录”，也不要接受占位路径、绝对路径或另一个日期的记录。
5. **checker 失败要早于构建和提交**：解析复核记录的守门脚本应该在构建、commit、push、发帖、上传之前运行；失败时输出缺哪个字段，而不是继续做副作用前置工作。

## 示例

一份最小发布门禁可以压缩成六个硬门禁和一个最终决策：

```text
Publish gate
- Site URL confirmation: Go
- Contact / subscription confirmation: Go
- Content decision: Go
- Authorization confirmation: Go
- Remote confirmation: Go
- Workspace boundary: Go
- No-push rehearsal result: Pass
- Final decision: Publish
```

对应的发布脚本不要自己猜测：

```bash
./scripts/check_publish_review_gate.py docs/publish-review-2026-08-11.md
./scripts/publish_daily.sh 2026-08-11 \
  --site-url "$PUBLIC_SITE_URL" \
  --review-note docs/publish-review-2026-08-11.md \
  --push
```

checker 的放行语义要非常窄：

```text
ALLOW only if:
- Final decision == Publish
- all hard gates == Go

BLOCK if:
- final decision is Dry-run only / Wait / empty
- any hard gate is Review / Wait / No-Go / missing
- rehearsal is Pass but final decision is not Publish
- review note path is placeholder, non-canonical, absolute, or auto-selected
```

如果复核记录里写了“本地 rehearsal 已通过，但还没人工授权 push”，checker 必须输出 `PUBLISH_BLOCKED`；这不是错误，而是正确吸收边界。

## 坑

- **把 dry run 当授权**：dry run 证明构建流程能跑，不证明用户允许外发。
- **把自动证据提升为 `Go`**：脚本发现 URL 或 remote 只能说明“有证据可审”，不能说明目标渠道、账号和观察窗口已经获批。
- **自动选最新复核记录**：无人值守脚本选错日期或选中 dry-run sample，会把历史记录误用于当前发布。
- **允许占位字段通过**：`<origin url>`、`example.com`、`approval pending`、`TODO`、`待填写` 必须是 `No-Go` 或 `Wait`。
- **checker 放在 push 之后**：如果先 commit / upload 再检查复核记录，门禁已经失去意义。
- **最终报告只说“已检查”**：报告必须写出 review note 路径、checker 结果和未触发的副作用边界。

## 检查

提交发布链改动前，逐项确认：

- 复核记录是否有固定字段名、合法取值和默认保守值？
- 六个硬门禁的 `Go` 是否都来自人工确认，而不是脚本猜测？
- 是否存在单独的 `Final decision: Publish`，且 rehearsal / regression / build 结果不能替代它？
- `--push` 是否要求人工显式传入 canonical review note 路径，不自动选最新文件，且发布日期、review note 文件名日期、checker 命令路径和发布命令日期一致？
- checker 是否在构建、commit、push、发帖、上传前执行，失败时能列出缺失字段？
- 测试是否覆盖：dry-run sample 阻断、rehearsal Pass 不解锁、缺任一硬门禁不解锁、最终 Publish + 全部 Go 才放行？
- notebook 或最终报告是否写清没有自动创建 remote、没有开启托管页面、没有外发推广、没有 push 的边界？
