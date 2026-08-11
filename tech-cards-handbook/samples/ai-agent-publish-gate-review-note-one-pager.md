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
