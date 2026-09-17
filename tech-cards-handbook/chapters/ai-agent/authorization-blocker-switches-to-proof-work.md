# Authorization blocker switches to proof work

## 问题

无人值守 Agent 经常会把“等用户授权发布/外联/收费”误当成“继续完善交付物”的理由：多写一个 landing page、多做一版报价、多补一个模板。结果是本地资产越来越厚，却没有真实渠道、联系人、观察窗口或支付/留资入口，下一轮仍然卡在同一个人类决策上。

## 要点

- **授权缺口不是内容缺口。** 如果缺的是渠道、账号、联系路径、目标受众或观察窗口，就不要再扩写 launch copy、交付包或价格表。
- **先固定等待请求。** 把需要人类回答的字段压成一段可转发请求，后续重复 surfaced 同一请求，而不是每轮换一种说法制造漂移。
- **无人值守默认切换到 proof work。** 当授权缺口无法自动补齐时，转向本地可验证的代码质量、检查脚本、文档索引、样本 smoke test 或读者资产；不要假装已经做了市场验证。
- **只在事实变化时更新 dashboard。** 只有真实渠道授权、可用 URL、真实脱敏反馈、检查失败或用户改选 offer，才改推荐决策；普通思考不应刷新“Last verified”来制造进展感。
- **最终报告分清 blocked 与 progressed。** 写清哪个 offer 仍 blocked by authorization，以及本轮改为推进了哪个可验证切片。

## 示例

本地 dashboard 已经写明某个 offer 缺少发布授权：

```text
Offer: personal assistant configuration service
Local proof: scope, intake, sample blueprint, landing page
Missing: channel/account, target audience, response route, 24h/48h window
Decision: Wait for channel authorization
```

错误做法是继续生成“第 3 版首发帖”和“第 4 版套餐说明”。正确做法是：

```text
1. 保持授权请求不变：列出 channel/account/contact/target/window 五个字段。
2. 不执行 publish、DM、push 或 paid listing 创建。
3. 切到 clean repo 的 proof work：例如补一个 smoke test、修一个文档链接、写一张可复用的运行边界卡片。
4. notebook 记录：offer blocked; replacement work completed; 回到 offer 的条件是真实授权字段已补齐。
```

如果后续用户只说“可以发一下试试”，但没有指定账号、渠道、联系人或观察窗口，仍然不能把它升级成发布许可；先回到固定字段请求。

## 坑

- 把“还没授权”理解成“交付物还不够好”，于是继续堆模板。
- 在 cron / scheduled job 里自动外发消息、创建付费链接或伪造公开 URL。
- 每轮改写 dashboard 的时间戳，却没有任何新的外部证据。
- 把 waitlist、草稿、样例页面说成真实购买信号。
- 最终报告只写“继续等待授权”，没有说明本轮实际推进了什么可验证资产。

## 检查

- 当前 blocker 是人类授权字段，还是本地交付物缺口？
- 是否已经有一段稳定的授权请求可以直接转发？
- 本轮有没有避免外发、发布、收费、push 等需要授权的动作？
- 替代任务是否有明确文件变更和验证命令，而不只是 notebook？
- 回到 offer 的条件是否写成可观察事实：授权字段齐备、真实 URL 出现、真实反馈进入，或用户明确改选实验？
