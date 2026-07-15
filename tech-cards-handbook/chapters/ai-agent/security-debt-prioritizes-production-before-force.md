# 安全债先分生产风险，不要默认 `audit fix --force`

**问题**：依赖审计出现高危漏洞时，Agent 为什么不能直接执行 `npm audit fix --force` 或一次性升级所有包？因为 force fix 往往把生产依赖、开发工具链、native 模块和 major breaking change 混在一起；如果没有先区分生产风险和验证半径，修安全债会变成不可归因的大升级，下一轮只剩“看起来更安全、但不知道哪里坏了”。

**要点**：

- 先把审计结果拆成两张表：`生产运行风险`（例如服务端运行依赖、数据库驱动、调度器、HTTP client）和 `开发链路风险`（例如 bundler、lint、test runner、transpiler）。
- 对生产依赖优先看是否能在同一 major 或小范围 direct dependency 升级中消除漏洞；只有验证链覆盖运行路径时，才接 native module、数据库驱动或调度器的 major 升级。
- 对开发依赖按工具链拆分：先处理 build/dev-server 暴露面，再处理 lint/test 规则升级；不要把 Vite、ESLint、TypeScript、测试框架一次性混升。
- `--force` 是最后选择，不是默认动作；执行前必须写清会引入哪些 major、哪些 API 或配置可能 breaking、失败后如何回滚。
- 每个安全债切片都要有验证出口：`audit` 结果、目标测试、全量 build、必要的 smoke test，以及提交后 clean status。

**示例**：

```text
Audit snapshot:
- npm audit --omit=dev: 9 vulnerabilities
- npm audit: 17 vulnerabilities

Triage:
1. Production direct dependency: node-cron -> uuid vulnerability.
   Hypothesis: upgrade node-cron 3 -> 4, current code only uses schedule().stop().
   Verification: backend tests + build + scheduler smoke/log check.
2. Production native dependency: sqlite3 -> node-gyp/tar chain.
   Hypothesis: upgrade sqlite3 only after checking Node/Docker compatibility.
   Verification: npm ci + backend tests + build + docker compose build.
3. Dev-only toolchain: vite/esbuild and typescript-eslint/minimatch.
   Hypothesis: split into Vite build chain first, ESLint rule chain second.
   Verification: frontend build + E2E list + lint baseline diff.

Decision:
Do not run npm audit fix --force globally. Pick one row, upgrade, verify, commit, then re-run audit.
```

**反例 / 修正做法**：

```text
反例：
- 看到 critical/high 就直接 npm audit fix --force。
- 把生产数据库驱动、前端 bundler、lint parser 和锁文件刷新放进同一个提交。
- 只报告“漏洞减少了”，不报告剩余漏洞属于生产还是开发依赖。
- native module 升级后只跑 TypeScript build，不跑安装、测试或容器构建。

修正：
- 先记录 audit --omit=dev 和完整 audit 的差异。
- 每次只接一个风险簇：HTTP client、scheduler、database driver、bundler 或 lint toolchain。
- 对每个簇写清 breaking-change 假设和最小验证链。
- 提交后再次读 audit、测试和 git status，作为下一轮接力输入。
```

**坑**：

- 把 vulnerability count 当成唯一目标：从 17 降到 0 如果靠大范围 force upgrade，可能引入比漏洞更难定位的行为变化。
- 忽略开发依赖的真实暴露面：dev-server、preview server 和构建插件也可能在本地或 CI 中处理不可信输入，但验证方式不同于生产运行依赖。
- 忽略 native 依赖安装路径：本地测试通过不代表 Docker、CI、Alpine、Node LTS 版本都能安装。
- 把锁文件刷新和 major 升级混在一起：先用小提交刷新兼容性数据，再单独做安全升级，回滚和复核都会更容易。
- 漏报剩余风险：如果暂缓 `--force` 项，必须说明它们为什么暂缓、属于生产还是开发、下一步第一条验证命令是什么。

**检查**：最终记录里是否同时出现了 `audit --omit=dev`、完整 `audit`、风险分组、是否使用 `--force` 的理由、每个升级切片的验证命令和提交后状态？如果只有“执行 audit fix，漏洞减少”，还没有完成可接力的安全债治理。
