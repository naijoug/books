# Path-scoped commit boundary prevents inherited dirty mix

## 问题

心跳式 Agent 在 dirty repo 里推进小任务时，最常见的事故不是改错代码，而是把“本轮可解释的 1 个文件”和“启动前已经存在的 10 个 dirty 文件”一起提交。即使验证命令通过，commit 也会把未知归属、未审校内容和本轮成果混在一起，后续无法判断该回滚哪一部分。

## 要点

- **先把启动状态当证据保存。** 规划前记录 `git status --short`，区分 `avoided paths` 和 `owned paths`，不要用最终状态倒推所有权。
- **只选择一个可解释的 owned slice。** owned slice 可以是一个新文件、一组同一功能的路径，或一个已经明确接管的 hunk；不能只是“同一个 repo 下的所有 dirty 文件”。
- **验证命令也要按路径收窄。** 对文档跑链接/索引检查，对代码跑目标测试；同时用 `git diff --check -- <owned paths>` 排除空白错误。
- **显式 path staging。** 提交前使用 `git add -- <owned paths>`，禁止 `git add .`、`git commit -am` 或 IDE 全量 staging。
- **读回 index，而不是相信自己。** `git diff --cached --name-only` 必须只显示 owned paths；如果出现启动前 dirty path，先 unstage 并重写提交范围台账。
- **最终报告同时写 included / excluded。** 交付不是只报 commit hash，还要说明哪些启动前 dirty path 没接管。

## 示例

一次 path-scoped 收尾可以用下面的命令梯：

```bash
# 1. 启动快照
git status --short

# 2. 只检查本轮 owned paths
git diff --check -- tech-cards-handbook/chapters/ai-agent/path-scoped-commit-boundary.md
python3 scripts/verify_tech_cards.py --full-only

# 3. 只 stage 本轮路径
git add -- tech-cards-handbook/chapters/ai-agent/path-scoped-commit-boundary.md \
  tech-cards-handbook/chapters/ai-agent/README.md \
  tech-cards-handbook/chapters/README.md \
  tech-cards-handbook/README.md

# 4. 读回 staged 边界
git diff --cached --name-only

# 5. 提交后再读回状态
git commit -m "Add path-scoped commit boundary card"
git status --short
```

对应的提交范围台账：

```text
Included paths:
- tech-cards-handbook/chapters/ai-agent/path-scoped-commit-boundary.md
- tech-cards-handbook/chapters/ai-agent/README.md
- tech-cards-handbook/chapters/README.md
- tech-cards-handbook/README.md

Excluded dirty paths:
- ai-personal-growth/README.md
- ai-personal-growth/chapters/07-side-hustles-and-income-diversification.md
- ai-personal-growth/chapters/appendix.md

Verification:
- git diff --check -- <included paths>
- python3 scripts/verify_tech_cards.py --full-only
```

## 坑

- 看到 `git status` 里有同目录文件，就默认它们都属于本轮。
- 为了“让 repo 干净”顺手提交启动前 dirty path。
- 用 `git add .` 后只看 commit message，不读回 `git diff --cached --name-only`。
- 验证命令覆盖了全 repo，就误以为全 repo dirty 都可以提交。
- notebook 只写“已提交”，没有列出 excluded dirty paths。

## 检查

- 是否在规划前记录了启动 `git status --short`？
- 是否写清本轮 owned paths 和 avoided paths？
- 是否用 path-limited `git diff --check -- <owned paths>` 或目标测试验证？
- staged path 是否由 `git diff --cached --name-only` 读回，而不是凭记忆确认？
- commit 后最终报告是否同时包含 commit hash、included paths 和 excluded dirty paths？
