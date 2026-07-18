# Artifact smoke test checks contract, not just existence

## 问题

交付物打包脚本常常用一句 `test -f product.zip` 当 smoke test。这个检查只能证明“生成了一个文件”，不能证明 zip 内目录结构稳定、必需文件齐全、禁止文件没有混入、输出目录没有残留，也不能阻止 tracked artifact 悄悄漂移。结果是命令看起来绿了，真正交付给读者或客户时才发现 README 丢失、路径多了一层、临时文件进包或示例无法按说明运行。

## 要点

- **先写交付契约，再写存在性断言。** smoke test 至少覆盖产物名、归档内根目录、关键入口文件、禁止文件和输出目录残留。
- **把 zip 当作可检查文件系统。** 通过 `unzip -Z1` / `tar -tf` / 语言标准库列出清单，再对清单做允许项和必需项断言。
- **检查说明入口能闭环。** 如果交付说明要求用户打开 `README.md`、运行 `scripts/check.sh` 或复制某个模板，smoke test 要确认这些路径在包内存在且位置正确。
- **禁止本地噪音进包。** `.git/`、`.DS_Store`、`node_modules/`、临时 staging、测试输出和本机绝对路径都应被显式排除或断言不存在。
- **存在性检查只作为最后一层。** `test -f product.zip` 可以保留，但它不能替代结构、内容和无残留契约。

## 示例

Shell smoke test 可以先把 zip 清单保存下来，再检查契约：

```bash
out_dir="$(mktemp -d)"
bash scripts/package-workflow-templates.sh --out-dir "$out_dir"

zip_path="$out_dir/workflow-templates.zip"
test -f "$zip_path"

listing="$out_dir/listing.txt"
unzip -Z1 "$zip_path" > "$listing"

grep -qx 'workflow-templates/README.md' "$listing"
grep -qx 'workflow-templates/templates/daily-review.md' "$listing"
! grep -q '^workflow-templates/.git/' "$listing"
! grep -q '\.DS_Store$' "$listing"
test ! -e "$out_dir/workflow-templates"
```

如果交付物带有示例命令，再把清单检查和最小运行检查分开：

```bash
extract_dir="$(mktemp -d)"
unzip -q "$zip_path" -d "$extract_dir"
(
  cd "$extract_dir/workflow-templates"
  test -f README.md
  test -d templates
)
```

## 反例 / 修正

反例：

```bash
bash scripts/package-prompt-handbook.sh --out-dir dist
test -f dist/prompt-handbook-standard.zip
```

这条测试在以下情况下仍会通过：zip 内多了一层 `dist/`，README 丢失，`.DS_Store` 被打进去，或 `dist/prompt-handbook-standard/` staging 目录残留。

修正：

```bash
out_dir="$(mktemp -d)"
bash scripts/package-prompt-handbook.sh --out-dir "$out_dir"
unzip -Z1 "$out_dir/prompt-handbook-standard.zip" > "$out_dir/listing.txt"

grep -qx 'prompt-handbook-standard/README.md' "$out_dir/listing.txt"
grep -qx 'prompt-handbook-standard/prompts/index.md' "$out_dir/listing.txt"
! grep -q '^prompt-handbook-standard/.git/' "$out_dir/listing.txt"
! grep -q '/tmp/' "$out_dir/listing.txt"
test ! -e "$out_dir/prompt-handbook-standard"
```

## 坑

- 只检查 zip 存在和非空，导致错误的目录层级、缺失入口文件和本机垃圾文件都能漏过。
- 把清单断言写得太宽，例如 `grep README`，结果 `docs/old-readme.md` 也能通过；关键入口应使用精确路径。
- 在真实 `dist/` 里测试，失败后留下残留；smoke test 应用临时输出目录，最后再断言真实输出命令的可移植路径。
- 只做允许项白名单，不给扩展文件留空间；对产品包可以采用“必需项 + 禁止项 + 根目录稳定”的组合，避免每次加模板都要大改测试。
- 忽略归档内路径里的临时目录或绝对路径；打包命令应从 staging root 进入后压缩稳定顶层目录。

## 检查

- smoke test 是否检查了归档内根目录、关键入口文件和至少一类禁止文件？
- 是否断言 `--out-dir` 下没有 staging 残留，而不仅是 zip 存在？
- 是否使用临时输出目录执行测试，避免污染 repo 的真实 `dist/`？
- 清单断言是否使用精确路径，避免误匹配同名文件？
- 如果交付说明包含“打开 / 复制 / 运行”的第一步，测试是否证明这些路径在包内按说明存在？
