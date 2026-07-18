# Tracked artifact needs drift check, not just regeneration

## 问题

有些可交付资产会同时保留源码目录、打包脚本和已生成的样例产物或站点文件。Agent 修完脚本后，如果只运行一次打包命令，很容易漏掉两个风险：一是 tracked artifact 仍然是旧版本，二是命令每次运行都会改出不同结果。最终表现为本地测试绿了，但仓库里的交付物、示例截图或发布目录并没有跟着更新，下一轮接力也不知道哪些差异是预期生成物，哪些是漂移。

## 要点

- **把生成物当成契约的一部分。** 只要仓库选择追踪 zip、静态页、样例输出或 manifest，就要检查它是否由当前脚本可复现地产生。
- **分清“生成成功”和“仓库无漂移”。** 打包命令返回 0 只能证明本次生成成功；还要用 `git diff --exit-code -- <artifact>` 或清单 hash 证明 tracked artifact 没有意外变化。
- **先用临时目录验证结构，再决定是否刷新 tracked artifact。** 临时输出适合 smoke test；真实输出目录适合确认仓库中应提交的产物是否需要更新。
- **提交时把源码、脚本、测试和被刷新产物放在同一范围台账里。** 如果 artifact 是本轮预期变化，notebook 要说明生成命令和差异归属；如果不是预期变化，先停下来查原因。
- **让漂移检查有稳定失败语义。** 失败要能回答：是需要提交新产物、生成不确定、脚本污染输出目录，还是测试输入不完整。

## 示例

先用临时目录检查交付契约，再用真实输出目录做漂移判断：

```bash
# 1. 临时目录：证明包结构正确，且不污染输出目录。
out_dir="$(mktemp -d)"
bash scripts/package-workflow-templates.sh --out-dir "$out_dir"
unzip -Z1 "$out_dir/workflow-templates.zip" > "$out_dir/listing.txt"
grep -qx 'workflow-templates/README.md' "$out_dir/listing.txt"
test ! -e "$out_dir/workflow-templates"

# 2. 真实目录：证明 tracked artifact 和当前脚本一致。
bash scripts/package-workflow-templates.sh --out-dir dist
git diff --exit-code -- dist/workflow-templates.zip
```

如果 zip 二进制差异不稳定，可以生成可比较的清单或 manifest：

```bash
unzip -Z1 dist/workflow-templates.zip | LC_ALL=C sort > dist/workflow-templates.manifest
git diff --exit-code -- dist/workflow-templates.manifest
```

## 反例 / 修正

反例：

```bash
bash scripts/package-prompt-handbook.sh --out-dir dist
bash tests/test-package-prompt-handbook.sh
```

这组命令可能让测试通过，却没有说明 `dist/prompt-handbook-standard.zip` 是否是本轮应提交的变化，也没有说明脚本是否每次生成同一个清单。

修正：

```bash
bash tests/test-package-prompt-handbook.sh
bash scripts/package-prompt-handbook.sh --out-dir dist
git diff --check -- scripts/package-prompt-handbook.sh tests/test-package-prompt-handbook.sh
git diff --exit-code -- dist/prompt-handbook-standard.zip || {
  echo "tracked package drifted; inspect and either commit refreshed artifact or fix nondeterminism" >&2
  exit 1
}
```

## 坑

- 把 `git status` 里出现的 generated artifact 一律当成噪音删除，结果丢掉本轮真正应该刷新的交付物。
- 只在临时目录跑测试，不检查仓库追踪的发布目录；测试绿了，用户实际下载的文件仍是旧的。
- 直接提交二进制 zip 差异，却没有写生成命令、结构清单或版本原因，下一轮无法判断是否可复现。
- 忽略 zip 时间戳、文件顺序、权限位等非业务差异；必要时改脚本，让清单排序、时间戳或 manifest 稳定。
- 在 dirty workspace 中把启动前 artifact 差异和本轮脚本变化混在一起提交；应先记录启动快照，再只接管自己能解释的路径。

## 检查

- 仓库是否追踪任何由脚本生成的 zip、静态页、manifest、示例输出或发布目录？
- 本轮是否同时证明了“临时输出结构正确”和“tracked artifact 没有非预期漂移”？
- 如果 artifact 变化是预期的，notebook 是否写清生成命令、相关源码/脚本和提交范围？
- 如果 artifact 变化不是预期的，是否先查明 nondeterminism、残留污染或启动前 dirty 归属，而不是直接提交？
- 最终报告是否把 artifact 检查结果和未接管的生成物差异分开说明？
