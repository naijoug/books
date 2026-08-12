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
6. **测试夹具要共享 canonical 证据**：正向放行、缺 remote、缺字段等 fixture 不要各自复制一份 review note、URL artifact 或 stub build；把这些证据写入 helper，防止门禁字段改名时只有部分测试更新。
7. **fixture 字符串只能有一个来源**：发布日期、站点 URL、canonical review note 路径、wrong-date 路径、dry-run sample 路径和预期错误信息要从同一组变量派生；不要在命令、断言和错误消息里重复手写。
8. **正向 fixture 也要断开生产环境**：`PUBLISH_ALLOWED` 只允许测试走到受控边界；临时仓库必须覆盖 token、remote、部署 CLI 和 artifact 目录，不能把真实发布环境当测试夹具。
9. **阻断 helper 必须三联断言**：URL、授权、review note、remote 等 guard 的公共 helper 不能只判断“失败了”；它必须同时检查退出码非 0、输出包含具体可行动原因、并且没有进入 build / commit / push 前置步骤。

## 示例

一份最小发布门禁可以压缩成六个硬门禁和一个最终决策；如果要把 checker 接入 `--push`，先回到样本页的“Checker 回归矩阵”，至少跑通 dry-run sample、rehearsal-only-pass、missing-one-gate、auto-evidence-review、wrong-note-date 和 publish-all-go 六类 fixture，再把命令写入发布 runbook。测试 fixture 里不要重复手写 canonical review note、站点 URL artifact 或 stub build 脚本：把这些证据集中到 `write_publish_review_note`、`write_site_url_artifacts`、`write_stub_build_tools` 这类 helper 中，让缺 remote 和正向 no-op publish 共享同一份放行证据。再把 `fixture_date`、`fixture_site_url`、`fixture_review_note`、`fixture_wrong_date` 和 `fixture_canonical_review_note_message` 放到测试顶部，由它们生成 CLI 参数和 `grep -F` 断言；这样把发布日期从 `2026-08-07` 改成下一期时，只需要改一个变量，而不会出现路径、错误消息和 summary 断言互相漂移。

正向 fixture 仍然要像阻断 fixture 一样写副作用边界：在临时仓库中清空生产 token，把 `origin` 指向本地 fake remote 或故意缺失，用 stub `wrangler` / `gh` / `send` 命令抢在真实 CLI 前面，并把 RSS、sitemap、JSON-LD、review note 写进测试目录。即使 checker 输出 `PUBLISH_ALLOWED`，测试也只能停在 no-op、no changes to commit、本地 fake remote 或 stub push；如果断网、删除生产 token 后测试不能稳定通过，说明它验证的是环境而不是发布闸门。

阻断 helper 要把失败语义也固定住，例如 `assert_rejects_guard_before_build(label, status, expected, output)` 不只是复用 shell 代码，而是把三件事锁在一起：命令必须非 0、错误消息必须点名缺的是 URL / 授权 / review note / origin 之一、输出里不得出现 `building`、`committing`、`uploading`、`pushing` 等副作用前置日志。新增 guard 时先复用这个 helper，再补一条只属于该 guard 的最小命令；如果 helper 只检查非 0，未来很容易出现“被别的错误挡住了，但测试仍绿”的假安全。

一份 review note 中的字段可以保持这么窄：

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
- **fixture 各自复制证据**：多个测试各写一份“可发布” review note 或站点 artifact，后续字段调整时容易出现 A 测试还在旧字段、B 测试已经新字段的假绿；共享 helper 比复制粘贴更接近真实发布证据。
- **fixture 字符串散落在三处**：CLI 参数、checker 错误消息和 readiness summary 断言如果各写一遍 `docs/ai-daily-publish-review-2026-08-07.md`，下一次换日期时很容易只改命令不改断言；日期、URL 和 canonical path 必须从同一组变量生成。
- **正向 fixture 继承生产环境**：为了让 `PUBLISH_ALLOWED` 场景通过而读取真实 token、沿用开发机 remote、调用真实部署 CLI 或写生产 artifact 目录，会把测试从“证明门禁”变成“试探生产环境”；正向路径也必须 stub、fake、local-only。
- **阻断 helper 只看退出码**：URL guard 因权限缺失失败、review note guard 因脚本路径缺失失败、remote guard 因 build 报错失败，都会得到非 0；如果不同时断言具体消息和未进入 build，测试会把错误的阻断原因当成正确门禁。

## 检查

提交发布链改动前，逐项确认：

- 复核记录是否有固定字段名、合法取值和默认保守值？
- 六个硬门禁的 `Go` 是否都来自人工确认，而不是脚本猜测？
- 是否存在单独的 `Final decision: Publish`，且 rehearsal / regression / build 结果不能替代它？
- `--push` 是否要求人工显式传入 canonical review note 路径，不自动选最新文件，且发布日期、review note 文件名日期、checker 命令路径和发布命令日期一致？
- checker 是否在构建、commit、push、发帖、上传前执行，失败时能列出缺失字段？
- 测试是否覆盖：dry-run sample 阻断、rehearsal Pass 不解锁、缺任一硬门禁不解锁、最终 Publish + 全部 Go 才放行？
- 正向和阻断 fixture 是否共享 canonical review note、站点 URL artifact、stub build helper，避免复制粘贴导致放行证据漂移？
- 发布日期、站点 URL、review note path、wrong-date path、dry-run sample path、预期 guard message 和 readiness summary 断言是否都从同一组 fixture 变量派生？
- 正向 fixture 是否显式覆盖生产 token、remote、部署 / 外发 CLI 和 artifact 目录，并能在断网、无生产凭据时只靠 stub / local fake remote 验证门禁？
- 阻断 helper 是否同时断言退出码非 0、输出包含 guard 的具体原因、且未进入 build / commit / upload / push 日志？
- notebook 或最终报告是否写清没有自动创建 remote、没有开启托管页面、没有外发推广、没有 push 的边界？
