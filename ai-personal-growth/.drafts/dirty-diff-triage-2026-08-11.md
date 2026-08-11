# 2026-08-11 既有 dirty diff 分诊记录

> 目标：只分诊启动前已经存在的 `ai-personal-growth` 三处未接管改动，不直接接管或改写正文；为下一轮决定“是否纳入正式书稿”留下可复核证据。

## 快照

- 目标 repo：`books/`
- 启动前 dirty paths：
  - `ai-personal-growth/README.md`
  - `ai-personal-growth/chapters/07-side-hustles-and-income-diversification.md`
  - `ai-personal-growth/chapters/appendix.md`
- 本轮处理方式：新增本分诊记录，不 stage 上述三处 dirty path。
- 主要风险：第 7 章 diff 同时包含内容结构压缩和大规模标点风格变化；若直接接管，容易把格式 churn 与真实审校收益混在一起。

## 文件级判断

| 文件 | diff 规模 / 性质 | 可取价值 | 风险 | 建议 |
|---|---|---|---|---|
| `ai-personal-growth/README.md` | 1 行审校状态更新 | 与附录 A.1 / A.14 的边界增强保持一致 | 依赖 `appendix.md` 是否最终接管；单独提交会造成状态先于正文 | 等 `appendix.md` 审校通过后一起接管，或保持不动 |
| `ai-personal-growth/chapters/appendix.md` | 小中等改动，强化 A.1、A.14 | 明确最小权限、人工确认点、验证证据、失败回退；与第 9-10 章和新加入的可验证交付闭环一致 | 仍是未接管 dirty diff，需要先做内容检查与引用检查 | 可作为下一轮优先接管候选；建议单独提交附录 + README 状态，不混入第 7 章 |
| `ai-personal-growth/chapters/07-side-hustles-and-income-diversification.md` | 658 行 diff，335 insertions / 383 deletions | 将 90 天路线压缩为阶段表，并保留外部证据闸门，读者行动路径更紧凑 | 大量中文全角标点被替换成半角 `, : ; ?`，标题冒号也被改成半角；这会破坏全书中文排版风格，并掩盖真实内容变化 | 暂不接管。若要接管，先拆成两步：1) 还原无意义标点 churn；2) 单独审校“90 天路线表格化”和外部证据闸门 |

## 第 7 章拆分建议

### 可以保留的候选内容

1. `7.10` 中把 90 天路线改成阶段表：
   - 优点：减少长段模板，降低重复度。
   - 需要检查：是否丢失原来“能力地图”“访谈记录”“标准化交付”的可复制模板感。
2. “外部证据闸门”小节：
   - 优点：主张清晰，能和 `books/tech-cards-handbook/chapters/ai-agent/publish-gate-fields-before-push.md` 的 gate 思维呼应。
   - 需要检查：术语是否与第 10 章的“可验证交付闭环”一致。

### 应避免直接接管的改动

- 将中文逗号、冒号、分号、问号批量替换为半角标点。
- 将中文引号替换为英文引号。
- 将列表结尾的中文分号批量替换为半角分号。
- 把提示词编号从 `①②③` 或中文编号改成紧贴数字的 `1...;2...`，可读性下降。

这些改动属于 format churn，不应和正文审校一起提交。

## 下一轮安全操作顺序

1. 先只看 `ai-personal-growth/chapters/appendix.md`：运行引用 / 绝对路径检查，判断是否可接管 A.1 和 A.14 的边界增强。
2. 如果接管附录，再同步 `ai-personal-growth/README.md` 的 1 行审校状态。
3. 第 7 章另开一轮：先生成只包含语义变化的 patch，排除标点 churn；再决定是否提交 90 天路线表格化。
4. 提交边界：每次只 stage 本轮确认过的文件，不把三处 dirty path 一次性全收。

## 最小验证清单

```text
python3 scripts/verify_ai_personal_growth_refs.py
git diff --check -- ai-personal-growth/chapters/appendix.md ai-personal-growth/README.md
git diff --check -- ai-personal-growth/chapters/07-side-hustles-and-income-diversification.md
```

人工复核标准：

- 不出现本机绝对路径、本机文件 URL 或临时目录。
- 中文正文保持全角标点风格，除英文术语、URL、命令和代码块外不批量改半角标点。
- README 的审校状态必须落后或等于实际已接管正文，不先行宣称完成。
