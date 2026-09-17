# 已部署不等于公开 GO，不要把 production 状态写成发布许可

**问题**：Agent 在项目里看到 `production 已部署`、public URL 可访问、CI 自动 deploy 或一次 smoke 记录时，为什么不能直接把文档改成“已上线 / 公开发布 GO”？

**要点**：

- 先拆成三个状态：`Deployed`（某个受控版本已经部署）、`Release evidence`（版本、migration、smoke、性能、回滚证据齐全）、`Public GO`（合规、内容授权、渠道、观察和责任人均已批准）。
- `production URL` 只能证明入口存在，不能证明当前版本、数据 schema、真实 AI、内容授权、儿童数据合规、渠道配置和回滚门禁都已关闭。
- 文档口径要允许“受控 Web 版本已部署，但公开发布仍 NO-GO”这种中间态；不要用一句“不能声明已上线”覆盖真实部署，也不要用“已部署”替代公开发布结论。
- 修改 release/checklist/README 前先找来源文件：Cloudflare / deploy 文档给部署事实，acceptance 文档给验收边界，release checklist 给公开 GO 门禁。不同来源冲突时，优先改措辞，不执行远端命令补证据。
- 最终报告和 notebook 要写清本轮没有执行 migration、deploy、remote smoke 或外部发布；只是把状态词对齐到已有证据。

**示例**：

```text
已有证据：
- `docs/deployment/cloudflare.md` 写明 production 已部署用户名/密码 Web 闭环。
- `README.md` 仍写“公开生产环境 NO-GO / 本结论仅代表本地闭环”。
- `docs/testing/acceptance.md` 写“不能声明已经上线”。

正确改法：
- README 增加 `Production Web: 已部署受控版本`。
- 另设 `V1 公开发布 GO: NO-GO`，列出真实 AI、内容授权、微信渠道、远端 smoke、性能和回滚证据仍需关闭。
- acceptance 文档改为“若另有 production 部署证据，也只能声明受控 Web 版本已部署，不能声明 V1 公开发布 GO 或可处理真实儿童作业”。
- 不运行远端 deploy / migration；不把文档措辞修正包装成发布完成。
```

**反例 / 修正做法**：

```text
反例：
- 看到 production URL 后，把 README 改成“已上线，可公开使用”。
- 看到 release checklist 仍 TODO 后，又把 Cloudflare 文档里的 deployed 事实删掉。
- 为了让两份文档一致，在无人值守 cron 里尝试执行 remote smoke 或 deploy。

修正：
- 保留部署事实：`受控版本已部署`。
- 保留发布边界：`公开发布 GO 仍 NO-GO`。
- 只做文档口径对齐；远端动作必须等待明确授权和 release checklist。
```

**坑**：

- **把 URL 当版本证据**：URL 可访问不说明当前 commit、migration 和 smoke 都对应本轮。
- **把本地 MVP GO 当公开 GO**：本地端到端闭环证明业务链路，不证明真实账号、真实 AI、儿童数据合规或渠道发布。
- **删除真实部署事实来维持保守**：安全边界不是否认已发生的部署，而是限制可声明的结论。
- **无人值守补跑远端命令**：为了补证据而执行 migration、deploy、smoke 会改变生产状态，必须有授权。
- **只改一个入口**：README、Cloudflare 文档、验收文档和 release checklist 对同一状态使用不同词，会让下一轮 agent 误判是否该发布。

**检查**：改生产/发布状态文档前，先回答五句：当前事实是 `Deployed`、`Release evidence` 还是 `Public GO`；部署事实来自哪份文档或命令输出；公开 GO 还缺哪些门禁；本轮是否只改文档措辞且没有执行远端副作用；最终报告是否明确写清“受控部署事实”和“公开发布 NO-GO”同时成立。
