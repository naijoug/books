# 多会话控制台先建台账，不要让 Agent 会话互相抢方向

## 问题

AI 时代的程序员越来越少只启动一个线性 Agent：一个会话在修代码，一个会话在写文档，一个会话在跑审查，远程会话、cron 会话和本地 IDE 会话还可能同时存在。问题不在于会话多，而在于没有控制台：谁拥有哪个 repo、谁能动哪个 path、谁掌握外部权限、谁负责验证证据，常常只散落在聊天记录和终端输出里。

这张卡解决的问题是：当同一目标被多个 Agent 会话并行或接力推进时，先建立一张 `Session / Permission / Evidence / Handoff` 台账，再决定是否继续开新会话或接管已有改动。

## 要点

1. **先登记会话，再分配任务**：每个活跃会话至少写清目标、repo、owned paths、不可触碰路径和当前阻塞；不要只用“谁最近回复”决定控制权。
2. **权限和证据分开记录**：能读文件、能改文件、能提交、能发布、能使用外部账号是不同权限；验证命令、日志、commit hash 和发布 URL 是证据，不是权限本身。
3. **dirty workspace 是控制台输入**：启动前 `git status --short`、staged paths、未跟踪文件和后台进程都要进入台账；没有台账时不要让第二个会话“顺手修一下”。
4. **只给每个会话一个主线**：多会话适合拆分为“实现 / 审查 / 文档 / 发布准备”，不适合让两个会话同时改同一文件或争夺同一个发布闸门。
5. **交接要写下一条安全动作**：handoff 不是“看起来差不多了”，而是下一会话可以直接执行的命令、文件范围和停止条件。

## 示例

```text
Multi-session control ledger

Session A: implementation
- Goal: fix package smoke test contract
- Repo: loom
- Owned paths: tests/unit/packageSmoke.test.cjs, src/package/*
- Do not touch: docs/, summaries/openclaw/*
- Permission: local edit + test + path-scoped commit
- Evidence: npm test -- tests/unit/packageSmoke.test.cjs
- Handoff: if smoke test passes, ask Session B to review failure wording only

Session B: review
- Goal: review failure wording and release notes
- Repo: loom
- Owned paths: docs/release-note-draft.md
- Permission: read implementation diff, edit docs only
- Evidence: git diff -- docs/release-note-draft.md
- Handoff: do not commit code paths; return review notes or doc commit hash

Session C: publish preparation
- Goal: prepare publish brief
- Repo: docs
- Permission: draft only; no external publish
- Evidence: publish gate fields filled
- Handoff: wait for explicit channel/account/contact/window authorization
```

最小操作流程：

```text
1. Snapshot: collect git status for every involved repo.
2. List sessions: active / planned / blocked.
3. Assign one primary outcome per session.
4. Mark owned paths and excluded paths before any edit.
5. Record permission boundary separately from evidence boundary.
6. Run the narrowest verification for each session output.
7. Close with commit hash or explicit unverified handoff.
```

## 坑

- **把多开窗口当并行能力**：多个聊天窗口不能自动提高吞吐；没有 owned paths 和验证边界时，只会制造冲突。
- **让审查会话顺手修实现**：审查会话一旦改实现路径，就破坏了实现 / 审查分工；除非重新登记它的 owned paths 和验证责任。
- **把读取权限误当发布权限**：能读账号配置、草稿或 preflight，不代表可以使用账号对外发布。
- **只记录最终结论，不记录状态证据**：下一轮无法判断哪些 dirty paths 是启动前存在、哪些是本轮新增。
- **开新会话逃避失败输出**：验证失败后应先更新台账里的 blocker 和下一条安全命令，而不是再开一个会话试运气。

## 检查

提交或交接前检查：

- 是否有一张明确的 `Session / Permission / Evidence / Handoff` 台账？
- 每个会话是否只有一个主线目标，并写清 owned paths 与 excluded paths？
- 权限是否拆成读、写、提交、发布、外部账号使用，而不是一句“已授权”？
- 验证证据是否能复制给下一轮，不依赖本机绝对路径或临时聊天记忆？
- 如果存在 dirty workspace，是否保留启动快照和收尾快照？
- 如果要发布或联系外部对象，是否仍走外部发布授权卡，而不是让控制台台账替代授权？
- 最终报告是否分别列出本轮提交 hash、未接管会话/路径和下一条安全动作？
