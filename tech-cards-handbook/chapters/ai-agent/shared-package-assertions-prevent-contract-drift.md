# Shared package assertions prevent contract drift

## 问题

多个交付物打包脚本往往会各自复制一段 smoke test：检查输出目录无残留、命令输出不泄露临时路径、tracked zip 和 fresh zip 是否一致。短期复制最快，但几轮之后就会出现断言口径漂移：一个包检查隐藏文件，另一个包只检查 staging 目录；一个包要求 `created <out-dir>/...`，另一个包允许打印本机绝对路径；一个包有 tracked artifact 对比，另一个包忘了刷新提示。结果是同一类交付风险在不同产品包里被不一致地验证。

## 要点

- **先等重复证明稳定，再抽 helper。** 只有当两到三个 package smoke test 已经验证过同一风险，才把断言抽成共享函数；不要在第一个包上预先设计大框架。
- **helper 只收敛通用契约。** 输出目录条目白名单、portable `created <out-dir>/...`、tracked/fresh zip 对比属于通用契约；包内关键文件、禁止文件、PDF header、产品说明仍留在各自测试里。
- **失败信息必须比复制代码更清楚。** 共享 helper 要接收 package label 和刷新命令，失败时输出 tracked-only、rebuilt-only、content-changed 等分类，避免调用方只看到“assert failed”。
- **保留每个包的交付语义。** `--with-pdf` 允许 zip + PDF，service provider 包只允许 service zip，legacy 包可能不是 tracked=fresh 语义；这些差异不要硬塞进同一个 helper。
- **抽象后必须横向回归。** 修改 helper 等于同时修改多个交付物的验证边界，提交前至少跑所有调用它的 package smoke test。

## 示例

共享 shell helper 可以把“输出目录只能包含最终产物”收束成一个函数：

```bash
assert_output_dir_entries() {
  local out_dir="$1"
  shift
  local expected=("$@")
  local actual=()

  shopt -s nullglob dotglob
  for entry in "$out_dir"/*; do
    actual+=("$(basename "$entry")")
  done
  shopt -u nullglob dotglob

  if [ "${#actual[@]}" -ne "${#expected[@]}" ]; then
    printf 'unexpected output entries in %s:\n' "$out_dir" >&2
    printf '  %s\n' "${actual[@]}" >&2
    exit 1
  fi

  for name in "${expected[@]}"; do
    printf '%s\n' "${actual[@]}" | grep -qx "$name" || {
      echo "missing expected output entry: $name" >&2
      exit 1
    }
  done
}
```

调用方仍然写清本包的交付物数量和名称：

```bash
out_dir="$(mktemp -d)"
output="$(bash scripts/package-workflow-templates.sh --out-dir "$out_dir" --with-pdf)"

assert_output_dir_entries "$out_dir" "AI工作流模板包.zip" "AI工作流模板包.pdf"
assert_portable_output_created "$output" "$out_dir" "created <out-dir>/AI工作流模板包.zip"
assert_zip_entries_match_tracked \
  "workflow templates package" \
  "packages/workflow-templates/AI工作流模板包.zip" \
  "$out_dir/AI工作流模板包.zip" \
  "bash scripts/package-workflow-templates.sh --out-dir packages/workflow-templates --with-pdf"
```

## 反例 / 修正

反例：四个测试各自复制一段类似逻辑，但允许项不同、错误信息不同、portable output 检查也不一致。

```bash
# test A
if [[ "$output" == *"$out_dir"* ]]; then exit 1; fi

# test B
test ! -e "$out_dir/package-staging"

# test C
python3 - <<'PY'
# compare tracked zip and rebuilt zip
PY
```

这会让新增包时靠复制粘贴选择一个“看起来差不多”的版本，风险口径继续漂移。

修正：先把通用断言放到 `tests/lib/package-output-assertions.sh`，再让每个 package test 只声明本包的 artifact 名称、tracked artifact 路径和刷新命令；包内 README、模板、禁止文件等仍在本测试里检查。

## 坑

- 为了减少重复，把所有 zip 内容检查都抽进 helper，导致测试文件读不出本包真正承诺交付什么。
- helper 不带 label 或 refresh command，失败时下一轮只能重新读脚本猜该怎么修。
- 把 legacy artifact、可选 PDF、多个子包输出强行统一成一个参数形状，反而隐藏交付语义差异。
- 抽 helper 后只跑一个调用方测试，漏掉另一个包的 shell 兼容性或文件名空格问题。
- helper 输出本机绝对路径，随后被复制进 `summaries/hermes/YYYY-MM-DD.md` 或最终报告，破坏可移植证据。

## 检查

- 至少两个 package smoke test 是否已经出现同类断言，并且风险语义确实相同？
- helper 是否只覆盖通用契约，而把包内关键入口、禁止文件和可选 artifact 留给调用方？
- 失败输出是否包含 package label、实际条目、差异分类和刷新命令？
- 抽象后是否跑完所有调用该 helper 的 package smoke test？
- notebook 和最终报告里的验证输出是否仍使用相对路径或 `<out-dir>` 这类可移植占位？
