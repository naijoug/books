# Appendix template changes need neighbor sync

## 问题

书稿、资料包或知识库里的附录模板经常成组出现：一个“使用前检查清单”、一个“工作流体检表”、一个“任务委派模板”可能都在描述目标、权限、人工确认、验证证据和失败回退。只增强其中一张模板，会让读者在不同入口复制到不一致的字段；更糟的是，后续 Agent 看到单个模板变强，可能误以为整组附录已经同步完成。

## 要点

- **先找邻近模板，而不是只看当前 hunk。** 附录里的 A.1、A.14、A.15 这类编号相邻模板，往往共享同一套边界字段。
- **把字段按语义对齐。** 不要求每张模板长得一样，但至少要确认目标、输入、权限、人工确认、验证证据、失败回退、沉淀资产这些字段是否各有落点。
- **区分模板增强和模板重写。** 新增一列“必留证据”属于字段增强；重排整张表、删掉原先的使用说明则属于结构改写，需要单独审。
- **不要跨未知 dirty ownership 提交。** 如果整组附录已经是启动前 dirty，本轮只能写邻近模板同步回执，除非明确接管整组修改。
- **提交前跑内容断言。** 附录类改动通常没有编译器保护，至少用脚本断言关键字段在目标模板中出现，并用 diff check 排除格式错误。

## 示例

只读接手附录模板增强时，可以先写一张邻近模板同步表：

```text
Template Neighbor Sync
- Changed template: books/ai-personal-growth/chapters/appendix.md#A.1 AI 使用前检查清单
- Neighbor templates: A.14 2026 年 AI 工作流体检表; A.15 Agent 任务委派模板
- Shared fields: 任务目标 / 输入材料 / 权限边界 / 人工确认点 / 验证证据 / 失败回退 / 可复用沉淀
- Current shape: A.1 and A.14 add permission, evidence and fallback fields; A.15 already has similar delegation fields
- Decision: Narrow / do not commit appendix dirty group until field alignment and ownership are explicit
- Next safe action: if taking ownership, make one commit for field alignment only, then another for wording or table structure
```

如果本轮真的接管，可以把最小验证写成：

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('ai-personal-growth/chapters/appendix.md')
text = p.read_text()
for phrase in ['权限边界', '人工确认点', '验证证据', '失败回退']:
    assert text.count(phrase) >= 3, phrase
print('appendix template neighbor sync checks passed')
PY
```

这类断言不是证明文案优秀，而是防止关键边界字段只出现在一张模板里。

## 反例 / 修正

反例：

```text
A.1 新增“失败回退” -> 看起来更安全 -> 提交整个 appendix.md
```

问题是 A.14 和 A.15 可能仍然缺同一字段，或者启动前 diff 还混有标点、结构、表格改写。最终 commit 名叫“完善模板”，实际却无法说明哪组字段被同步。

修正：

```text
先列出相邻模板 -> 标出共享字段是否存在 -> 只接管字段对齐这一个边界 -> 用内容断言和引用校验验证 -> 在 notebook 写清未接管的结构/标点改写
```

## 坑

- 只看新增行，不看同一附录里相邻模板是否还在使用旧字段口径。
- 把“表格多一列”误当作纯格式优化；新增证据、权限、回退字段实际会改变读者执行方式。
- 为了统一，把所有模板强行改成同一张表，丢掉每个模板自己的使用场景。
- 在启动前 dirty 的大附录里顺手修一个词，然后提交整份文件。
- 验证只跑全书链接，不断言关键字段是否真的在目标模板组中出现。

## 检查

- 是否列出了被改模板和至少一个相邻模板？
- 是否把共享字段按语义对齐，而不是只追求表头一致？
- 是否说明本轮是字段增强、结构重排、文案润色，还是三者混合？
- 如果目标附录启动前已经 dirty，是否避免把未知改动混入本轮提交？
- 是否用内容断言检查关键字段，并运行相关书稿 verifier / diff check？
