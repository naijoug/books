# Tech Cards Handbook Samples

本目录放可复制的 agent 输入、审查样例、一页纸模板和交接片段；它们不是正式卡片，不计入 `chapters/` 的卡片数。维护样本入口时，优先让读者能在 30 秒内回答：我该复制哪一份、它解决哪类接力风险、还需要回到哪张卡片补背景。

## 推荐入口

| 场景 | 先用 | 作用 |
|---|---|---|
| 完整 dirty workspace 接力：周期性唤醒的 Agent 面对 dirty workspace，需要完整 prompt、证据表和最终报告字段 | [`ai-agent-sample-pack.md`](ai-agent-sample-pack.md) | 9 张精选卡片建立最小闭环，附录和配套模板补足执行输入 |
| 只需要一页纸启动一次 dirty workspace 接力 | [`ai-agent-dirty-workspace-one-pager.md`](ai-agent-dirty-workspace-one-pager.md) | 压缩启动快照、归属判断、path-limited 推进和收尾报告 |
| 命令失败、测试失败或前置条件失败后需要改计划 | [`ai-agent-failure-absorption-one-pager.md`](ai-agent-failure-absorption-one-pager.md) | 把失败写成“信号 -> 影响 -> 证据位置”，再决定范围、顺序、目标或交接如何变化 |
| 轻量 proof：小改动需要先证明基础契约，再决定是否跑重型构建 | [`ai-agent-proof-checker-one-pager.md`](ai-agent-proof-checker-one-pager.md) | 设计轻量 preflight 的风险边界、命令顺序和 notebook 句式 |
| 验证清单太散，需要确定下一条最安全命令 | [`ai-agent-next-safe-command-ladder-one-pager.md`](ai-agent-next-safe-command-ladder-one-pager.md) | 把“跑哪些检查”改写成“当前最大风险 -> 下一条命令 -> pass/fail 语义” |
| 部分边界没有覆盖，但本轮验证没有失败 | [`ai-agent-unverified-handoff-one-pager.md`](ai-agent-unverified-handoff-one-pager.md) | 拆开已验证事实、未验证原因、结论措辞和下一步第一条动作 |
| 验证被失败阻断，需要把失败证据交给下一轮 | [`ai-agent-verification-failure-handoff-template.md`](ai-agent-verification-failure-handoff-template.md) | 固定“已验证 / 未验证 / 结论措辞 / 下一步 / 证据位置”字段 |
| 最终报告容易漏字段 | [`ai-agent-final-report-field-quickref.md`](ai-agent-final-report-field-quickref.md) | 核对成果、验证、notebook、commit hash、未接管边界和下一段接力点 |

## 使用顺序

1. **先选主入口**：完整接力用样本包，只做一次短接力用 dirty workspace 一页纸。
2. **再补风险模板**：失败多就用失败吸收；验证边界不清就用 proof checker、命令梯或未验证项交接。
3. **最后核对报告字段**：提交后用最终报告字段速查表，确保成果和排除边界同时可接力。

完整背景阅读见 [`../chapters/ai-agent/README.md`](../chapters/ai-agent/README.md) 的“3 分钟读法”和“快速路径：dirty workspace 心跳接力”。

## 维护检查

- 新增样本时，同步判断是否需要加入本索引、[`../README.md`](../README.md) 的样本包说明，以及 [`../chapters/ai-agent/README.md`](../chapters/ai-agent/README.md) 的配套输入段落。
- 链接或入口文案变更后运行：

```bash
python3 scripts/test_verify_tech_cards_links.py
python3 scripts/test_verify_tech_cards_index.py
python3 scripts/verify_tech_cards_links.py
python3 scripts/verify_tech_cards_index.py
```
