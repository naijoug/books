# AI Agent Publish Gate Review Note One-Pager

用途：当 agent 已经准备把日报、资料包、落地页、插件包或 beta 构建从 dry run 推到外部渠道时，用这页纸把“人工确认字段 + canonical review note + checker 输出 + 未触发副作用”压缩成一张可复制的发布闸门输入。它配套 [`../chapters/ai-agent/publish-gate-fields-before-push.md`](../chapters/ai-agent/publish-gate-fields-before-push.md)，重点不是更快 `--push`，而是让 `--push` 只能读取同一期、同一路径、同一套硬门禁的复核记录。

相关运行材料可参考 `makemoney/docs/ai-daily-release-checklist.md`、`makemoney/scripts/check_ai_daily_publish_review_gate.py` 和 `makemoney/scripts/publish_ai_daily.sh`。这里故意使用路径文本而不是书内链接，因为这些材料位于其他仓库，不属于本书链接校验范围。

## 30 秒入口判断

| 看到的信号 | 默认决策 | 立即写下的缺口 |
|---|---|---|
| 只有 dry-run / build / smoke pass | `PUBLISH_BLOCKED` | `Final decision: Publish` 与六个硬门禁 `Go` |
| 有 `No-push rehearsal result: Pass`，但最终决策仍是 dry run | `PUBLISH_BLOCKED` | `Final decision` |
| 有真实 URL / remote，但没有人工确认 | `PUBLISH_BLOCKED` | 对应 confirmation 字段 |
| 有人工确认，但 review note 路径不是 canonical | `PUBLISH_BLOCKED` | `Canonical review note path` |
| 有 canonical review note，但日期不等于本次发布日期 | `PUBLISH_BLOCKED` | `Review date match` |
| checker 输出 `PUBLISH_ALLOWED`，但没有明确外部副作用授权 | `Wait for authorization` | `Allowed command / channel / account` |
| checker 输出 `PUBLISH_ALLOWED`，且授权包完整 | `Ready for controlled publish` | `Evidence log path` |

默认规则：`PUBLISH_ALLOWED` 只说明复核记录字段满足门禁；它不替代渠道授权、账号授权、发布窗口或最终命令授权。缺任何一项时，本页交付物就是阻塞说明，而不是发布行为。

## Review note packet

```text
Release date:
Artifact / offer:
Canonical review note path: docs/publish-review-YYYY-MM-DD.md
Review date match: Go / No-Go / Wait
Checker command:
Checker output: PUBLISH_ALLOWED / PUBLISH_BLOCKED
Final decision: Publish / Dry-run only / Wait
Site URL confirmation: Go / No-Go / Wait
Contact / subscription confirmation: Go / No-Go / Wait
Content decision: Go / Fix / Wait
Authorization confirmation: Go / No-Go / Wait
Remote confirmation: Go / No-Go / Wait
Workspace boundary: Go / No-Go / Wait
No-push rehearsal result: Pass / Blocked / Not checked
Allowed side effects:
Do-not-touch side effects:
Evidence log path:
```

填写规则：

- `Canonical review note path` 必须是本次发布日期对应的相对路径；不要填绝对路径、dry-run sample、旧日期文件或“最新记录”。
- `Review date match` 只有在 `Release date`、review note 文件名日期、checker 命令中的路径日期和发布命令日期一致时才写 `Go`；任一日期为空、旧日期、跨日复用或靠“最新记录”推断时写 `No-Go` / `Wait`。
- 六个硬门禁的 `Go` 必须来自人工确认字段或人工编辑后的复核记录；自动探测到 URL、remote、干净工作区只能算证据，不能自己升级为 `Go`。
- `No-push rehearsal result: Pass` 只能证明本地页面、RSS、artifact 或 remote 证据已检查，不能替代 `Final decision: Publish`。
- `Allowed side effects` 必须逐项列出允许的动作，例如 commit、push、upload、post、send；没有列出的动作都写进 `Do-not-touch side effects`。
- `Evidence log path` 写后续能复查的记录位置，不写“见上文”。

## Readiness summary packet

当发布脚本已经输出 `readiness.*` 或 `cron.readiness.*` 字段时，把它们视为机器可读的交接契约，而不是附属日志。review note 决定“能不能发布”，readiness summary 说明“为什么当前状态是 allow / blocked / skipped / failed / published”。

```text
Release id / date:
Command mode: dry-run / push / cron
Readiness prefix: readiness / cron.readiness
Readiness decision: blocked / allowed / skipped / failed / published
Canonical review note path:
review_note_path:
review_note_canonical: not_required / matched / mismatch / missing
human_review_go: true / false
publish_authorized: true / false
site_url: missing / <relative evidence field>
public_url: missing / <url>
raw_freshness: checked_by_cron_when_compare_previous_raw_true / pass / fail / not_compared
collected_quality: pass / fail / not_checked
git_remote_origin: missing / present
Next safe command:
```

使用规则：

- dry-run 默认不要求 review note，但必须写出 `review_note_canonical=not_required`、`human_review_go=false`、`publish_authorized=false`，避免把 rehearsal pass 升级为授权。
- push 模式必须同时报告 `review_note_path`、`review_note_canonical`、`human_review_go` 和 `publish_authorized`；任一字段为空或 mismatch 时，下一步只能回到 canonical review note。
- skipped / failed 路径也要保留字段名；无法检查的项写 `not_checked` / `not_compared`，不要直接省略字段。
- `site_url`、`public_url`、`git_remote_origin` 是证据字段，不是人工授权字段；它们不能单独让 `publish_authorized=true`。
- `Next safe command` 必须是当前状态下第一条低风险动作，例如补 review note、重跑 checker、修 raw freshness、补质量数据或请求发布授权。

最小回归矩阵：至少覆盖 dry-run blocked、push 缺 review note、push 路径 mismatch、canonical review note 但人工字段未 Go、门禁失败、发布成功六条路径；每条路径都断言相同字段名仍出现。

## 发布脚本前置检查

```text
Expected command shape:
1. Run checker on the canonical review note.
2. Confirm checker prints PUBLISH_ALLOWED.
3. Run the publish command with the same review note path.
4. Stop before any unlisted side effect.

Example:
./scripts/check_publish_review_gate.py docs/publish-review-2026-08-11.md
./scripts/publish_daily.sh 2026-08-11 \
  --review-note docs/publish-review-2026-08-11.md \
  --push
```

脚本必须在 build、commit、push、upload、post、send 之前失败；失败输出要能说明是字段缺失、路径不 canonical、日期不匹配、最终决策不是 Publish，还是某个硬门禁不是 `Go`。

## Checker 回归矩阵

把 review note checker 接入 `--push` 之前，先用最小 fixture 跑下面 6 个场景。目标不是证明发布链完整，而是证明 checker 的失败语义足够窄：

| fixture | Final decision | 六个硬门禁 | rehearsal | 路径 / 日期 | 期望输出 |
|---|---|---|---|---|---|
| dry-run sample | `Dry-run only` | 至少一个 `No-Go` / `Wait` | `Blocked` / `Not checked` | canonical 或 sample 路径 | `PUBLISH_BLOCKED` |
| rehearsal-only-pass | `Dry-run only` | 全部 `Go` | `Pass` | canonical 且同日 | `PUBLISH_BLOCKED` |
| missing-one-gate | `Publish` | 一个硬门禁 `Wait` / 缺失 | `Pass` | canonical 且同日 | `PUBLISH_BLOCKED` |
| auto-evidence-review | `Publish` | 任一硬门禁仍是 `Review` | `Pass` | canonical 且同日 | `PUBLISH_BLOCKED` |
| wrong-note-date | `Publish` | 全部 `Go` | `Pass` | review note 日期不等于发布日期 | `PUBLISH_BLOCKED` |
| publish-all-go | `Publish` | 全部 `Go` | `Pass` | canonical 且同日 | `PUBLISH_ALLOWED` |

最小测试断言：每个阻断 fixture 都要检查退出码非 0，并断言输出里包含具体原因；唯一放行 fixture 要检查退出码为 0、输出来自同一份 review note，且测试本身不执行 build、commit、upload、post、send 或 push。

## Fixture helper 命名约定

把发布门禁测试拆成 helper 时，命名要体现“它生成证据”还是“它执行命令 / 断言边界”，避免 helper 继续藏副作用：

| helper 类型 | 命名示例 | 只允许做什么 | 不允许做什么 |
|---|---|---|---|
| canonical 证据写入 | `write_publish_review_note`、`write_site_url_artifacts` | 写同一期 review note、站点 URL、RSS / sitemap / JSON-LD 等最小 artifact | 自动改最终决策、创建 remote、触发 build |
| stub 工具准备 | `write_stub_build_tools`、`copy_publish_gate_scripts` | 复制待测脚本、放置不会外发的 stub 命令 | 调真实部署命令、读取用户环境中的生产 token |
| fixture 变量 | `fixture_date`、`fixture_site_url`、`fixture_review_note` | 生成 CLI 参数、canonical path、wrong-date path、expected message | 在断言里再手写另一份日期 / URL / path |
| 阻断断言 | `assert_did_not_reach_build`、`assert_rejects_guard_before_build` | 证明 checker / guard 在 build、commit、push 前失败 | 在失败路径里跑 build 或初始化 remote |
| 正向受控命令 | `run_publish_with_all_authorizations` | 只在临时仓库里跑带齐授权的 no-op / stub publish | 连接真实 remote、上传、post、send、push |

经验法则：`write_*` helper 只能准备文件，`assert_*` helper 只能检查输出和退出码，`run_*` helper 必须在名字里写清授权条件或 no-op 边界。这样后续新增 publish 渠道时，测试读者能从 helper 名字上看出哪里是证据、哪里是门禁、哪里可能产生副作用。

特别是正向命令 helper，不要只叫 `run_publish`。名字里至少要暴露三类边界：授权是否齐全、证据是否 canonical、外部副作用是否 stub / no-op。例如 `run_publish_with_all_authorizations` 说明它只负责“带齐授权字段后进入受控发布路径”；如果同一个 helper 还依赖本地 fake remote 或 no-op commit，就在调用点旁边断言 `no upload / post / send / push`，不要让读者误以为它可以复制到生产命令里直接执行。

## Fixture 副作用边界

发布门禁测试的正向 fixture 也只能证明“在临时环境中允许走到下一步”，不能借机碰生产环境。给每个 helper 加下面这些约束：

- 不读取生产 token：测试里显式清空或覆盖 `GITHUB_TOKEN`、`CLOUDFLARE_API_TOKEN`、邮件 / 社媒 / 支付渠道 token；需要 token 形状时只写 `fake-token-for-test`。
- 不继承真实 remote：临时仓库要么没有 `origin`，要么使用本地 bare repo / file URL；不要从开发者机器复制 `.git/config`。
- 不调用真实 CLI：`wrangler`、`gh`、`vercel`、`netlify`、邮件发送、社媒发布等命令必须用 stub 放在临时 `PATH` 前面，并在输出里写明 `stubbed`。
- 不复用生产 artifact 目录：站点 URL、RSS、sitemap、JSON-LD、review note 都写入测试临时目录；断言路径使用相对路径或临时仓库内路径。
- 不让 positive fixture 做真实 push：即使 `PUBLISH_ALLOWED`，正向测试也应停在 no-op、no changes to commit、本地 fake remote 或 stub push 的边界，并断言没有 upload、post、send。

一句话检查：如果把网络断开、删除所有生产 token、把 remote 指到不存在的位置，测试仍应能稳定验证门禁语义；否则它验证的不是 checker，而是在消耗真实发布环境。

## 阻塞时的最小交接句

```text
Decision: PUBLISH_BLOCKED. Review note path: docs/publish-review-YYYY-MM-DD.md. Missing / invalid fields: <list>. No-push rehearsal result does not unlock publish. No side effects were triggered: no remote creation, no Pages enablement, no upload, no post, no send, no push. Next safe command: fill or edit the canonical review note, rerun the checker, then request explicit authorization for the controlled publish command.
```

## 常见反模式

- 用 `all checks passed`、`smoke passed` 或 `rehearsal passed` 替代 `Final decision: Publish`。
- 让脚本自动选择最新 review note，或接受 `docs/publish-review-YYYY-MM-DD.dry-run-sample.md`。
- 把 URL / remote 探测结果直接写成 `Go`，没有人工确认来源。
- checker 通过后新增发布渠道、账号、价格、承诺或推广文案。
- 在 checker 之前先 commit、push、上传或发帖。
- 最终报告只说“已检查”，没有写 review note 路径、checker 输出和未触发副作用。

## 验收标准

一轮受控发布只有在下面条件同时满足时才可继续：

- review note 路径是本次日期的 canonical 相对路径，且由人工显式传入。
- `Review date match: Go` 明确确认发布日期、review note 文件名日期、checker 命令路径和发布命令日期一致。
- checker 输出 `PUBLISH_ALLOWED`，并且输出来自同一份 review note。
- `Final decision: Publish` 与六个硬门禁 `Go` 同时存在。
- `Allowed side effects` 与用户授权一致，未授权动作保持 `Do-not-touch`。
- 发布前后的 notebook / report 写清 checker 命令、输出、commit 或 artifact 证据，以及没有触发的副作用边界。

否则停止在复核记录或授权请求层，不进入外部发布。
