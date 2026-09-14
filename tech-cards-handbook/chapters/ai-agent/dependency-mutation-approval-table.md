# 依赖变更审批先共享测试表，不要让前后端规则各自漂移

## 问题

Agent 可以执行 shell 命令后，依赖变更不只来自 `npm install`。`npm ci`、`pnpm --filter web update`、`python -m pip uninstall`、`cargo remove` 都可能改变 lockfile、运行环境或构建结果。

如果前端只做字符串预扫描、后端只拦少数子命令，确认弹窗和真实执行策略会逐渐漂移：用户以为已经被提醒，后端却放行；后端要求审批，前端文案却只说 install，用户不知道 `remove` / `update` 的真实影响。

## 要点

- 先写共享测试表，再改解析逻辑；表里必须同时包含正例、反例和 monorepo/workspace 选项。
- 把风险命名成“依赖或环境变更”，不要把所有 mutation 都叫 `install`。
- 解析时找真实子命令：跳过环境变量、包管理器全局选项和 workspace 选择器；`python -m pip` 要从 `pip` 之后继续找。
- 前端预扫描只负责提前提示，后端执行策略才是兜底；二者都要跑同一批 fixture。
- 反例和正例同等重要：`npm run add-fixture`、`pnpm run update-docs` 这类脚本名不应因为包含 mutation 词就变成审批噪音。

## 示例

```text
共享 fixture：dependency-mutation-approval

需要审批：
- npm ci
- pnpm --filter web update
- yarn add react
- bun remove left-pad
- python -m pip uninstall requests
- pip3 install -r requirements.txt
- cargo add anyhow
- cargo remove anyhow

不需要审批：
- npm run add-fixture
- pnpm run update-docs
- yarn run upgrade-notes

前端 proof：commandLine.test 覆盖 detectDangerousCommand
后端 proof：execution_policy test 覆盖 assess_execution
文案 proof：approval prompt 显示 Risk: Dependency or environment change
```

实现时让 fixture 成为唯一判断来源：如果新增 `uv sync`、`pip install --upgrade` 或 `yarn workspace app remove lodash`，先把它们加入共享表，再分别补前端、后端和文案测试。这样失败会指向“哪一层没跟上”，而不是让下一轮靠记忆猜漏项。

## 坑

- 只匹配单词：看到 `install` / `update` 就拦，会误伤脚本名和文档命令。
- 只测 happy path：没有 `run` 脚本反例，后续 tightening 会把普通项目脚本变成审批噪音。
- 只改前端：真正执行命令的后端仍可能漏掉 `ci`、`remove`、`uninstall`。
- 只改后端：用户看不到风险类别，最终确认变成盲点确认。
- 不记录范围：依赖变更规则通常跨 TypeScript、Rust/Tauri、测试 fixture 和 UI 文案；提交前必须 path-limited stage，避免混入启动前 dirty path。

## 检查

- 共享测试表是否同时覆盖 `ci`、`add`、`install`、`remove`、`uninstall`、`update`、`upgrade` 以及至少一个 workspace/monorepo 选项？
- 每个正例是否在前端预扫描和后端执行策略里都要求审批？
- 每个反例是否明确保持不审批，且反例原因写清“真实子命令是 run”？
- 确认弹窗是否显示风险类别、严重度和原始命令，而不是只说 “requires approval”？
- 最终报告是否写清本轮 owned paths、未接管 dirty paths、聚焦测试命令和提交 hash？
