# Package staging stays outside output dir

## 问题

打包脚本常见写法是先在 `--out-dir` 下创建一个 `product-name/` staging 目录，再把它压成 `product-name.zip`。这样 zip 可能是正确的，但一次 smoke test 或发布命令会在输出目录留下未跟踪目录，污染 `git status`，也让下一轮 Agent 难以判断哪些文件是交付物、哪些只是临时中间产物。

## 要点

- **输出目录只放最终交付物。** `--out-dir` 的契约应该是“调用者要拿走的文件”，不是 staging、缓存和临时构建目录的混合区。
- **staging 用临时目录承载。** 用 `mktemp -d`、语言标准库临时目录或 CI workspace 的临时区构建包内容，脚本退出时用 `trap` / `finally` 清理。
- **归档内根目录可以保持稳定。** staging 不在输出目录，并不意味着 zip 里不能有 `product-name/` 顶层目录；只要在临时目录中创建这个根目录即可。
- **测试要断言无残留。** smoke test 不只检查 zip 存在，还要检查 `--out-dir` 下没有 staging 目录、临时文件和未声明产物。
- **日志保持可移植。** 打印输出路径时优先使用调用者传入的相对路径或 repo 相对路径，避免把临时目录绝对路径写进 notebook / release note。

## 示例

Shell 打包脚本可以把 staging 和输出目录分离：

```bash
out_dir="${OUT_DIR:-dist}"
package_name="prompt-handbook-standard"
zip_path="$out_dir/$package_name.zip"

mkdir -p "$out_dir"
staging_root="$(mktemp -d)"
cleanup() {
  rm -rf "$staging_root"
}
trap cleanup EXIT

package_root="$staging_root/$package_name"
mkdir -p "$package_root"
cp -R data/prompt-handbook/. "$package_root/"

(
  cd "$staging_root"
  zip -qr "$OLDPWD/$zip_path" "$package_name"
)

printf 'wrote %s\n' "$zip_path"
```

对应 smoke test 要覆盖“成功但污染输出目录”的反例：

```bash
out_dir="$(mktemp -d)"
bash scripts/package-prompt-handbook.sh --out-dir "$out_dir"

test -f "$out_dir/prompt-handbook-standard.zip"
test ! -e "$out_dir/prompt-handbook-standard"
find "$out_dir" -mindepth 1 -maxdepth 1 -type d | read -r leftover && exit 1 || true
```

## 反例 / 修正

反例：

```bash
package_root="$out_dir/prompt-handbook-standard"
rm -rf "$package_root"
mkdir -p "$package_root"
cp -R data/prompt-handbook/. "$package_root/"
zip -qr "$out_dir/prompt-handbook-standard.zip" "$package_root"
```

这会把 staging 目录留在 `dist/`，甚至可能把本机路径结构写进 zip。

修正：

```bash
staging_root="$(mktemp -d)"
trap 'rm -rf "$staging_root"' EXIT
package_root="$staging_root/prompt-handbook-standard"
# ...复制文件...
(cd "$staging_root" && zip -qr "$OLDPWD/$out_dir/prompt-handbook-standard.zip" prompt-handbook-standard)
```

## 坑

- 只在脚本开头 `rm -rf "$out_dir/product"`，但没有改变 staging 位置；这只能清旧残留，不能防新残留。
- zip 命令从 repo root 执行，导致归档内包含 `tmp/.../product` 或 `dist/product` 路径；应从 staging root 进入再压缩稳定顶层目录。
- 测试只断言 zip 文件存在，没有断言输出目录中“只剩允许的文件”。
- 在测试里使用项目真实 `dist/`，失败时留下脏文件；测试应使用临时 `--out-dir`。
- 为了隐藏临时目录，日志完全不打印产物路径；交接仍需要可复制的相对 zip 路径。

## 检查

- 打包脚本的 staging 目录是否位于 `mktemp` / 临时 workspace，而不是 `--out-dir`？
- 脚本是否用 `trap` / `finally` 清理 staging，即使复制或 zip 失败也会执行？
- zip 内是否仍有稳定的产品顶层目录，而不是临时路径或输出目录路径？
- smoke test 是否断言 `--out-dir` 下不存在 staging 目录和未声明产物？
- 运行脚本后 `git status --short` 是否不会因为输出目录残留而出现新的未跟踪目录？
