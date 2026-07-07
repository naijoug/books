# 先写人类假设，再让 Agent 动手

**问题**：AI 编程练习或短节拍任务中，如何避免 Agent 一上来接管判断，导致人类只剩下复制命令、粘贴结果，最后无法说明自己到底提升了什么？

**要点**：

- 在调用 Agent 生成方案或修改代码前，先写一句 `Human hypothesis before agent`：我认为问题在哪里、最小可改点是什么、验证应该如何变化。
- 假设不要求正确，但必须可被验证输出推翻；如果只是“让 Agent 看看”，就还没有进入刻意练习。
- Agent 的作用是扩展候选、补测试、检查遗漏，而不是替代初始判断；最终复盘要写出“Agent 没有替我拥有的那部分学习”。
- 如果验证失败，先比较失败输出和原假设的差异，再决定修假设、缩范围或切换任务。
- 适合和 [`failure-output-must-change-plan.md`](failure-output-must-change-plan.md)、[`delivery-budget-prevents-heartbeat-drift.md`](delivery-budget-prevents-heartbeat-drift.md) 以及 [`verify-before-optimistic-summary.md`](verify-before-optimistic-summary.md) 一起使用：先有人类假设，再有预算，再有验证。

**示例**：

```text
Practice target:
- 修一个脚本输出顺序的小问题，预算 30 分钟。

Human hypothesis before agent:
- wrapper 的标题晚于子进程输出，原因可能是 stdout buffering；最小修复是在 wrapper 的 print 上加 flush=True。
- 验证方式：mock print/subprocess.run 断言先 flush 再启动子进程；再跑真实 full-only verifier 看日志顺序。

Agent proposal summary:
- 只改 wrapper print，不碰 verifier 逻辑。
- 新增一个回归测试覆盖 heading print 的 flush 参数和调用顺序。

Verification:
- python3 scripts/test_verify_tech_cards.py
- python3 scripts/verify_tech_cards.py --full-only

What I learned that the agent did not own:
- 这不是“日志美化”，而是 proof 可读性问题；如果标题顺序不稳定，下一轮 Agent 会更难判断哪个输出属于哪个步骤。
```

**反例 / 修正做法**：

```text
反例：
- 直接要求 Agent “看看这个脚本有没有可以改进的地方”。
- Agent 提出 5 个重构点，本轮改了 3 个；最后只记录测试通过。

问题：
- 没有人类假设，所以不知道哪些改动来自自己的判断，哪些只是 Agent 扩写。
- 任务从一个可验证小题漂移成泛化重构。

修正：
- 先把问题压成一句可证伪假设：例如“失败输出缺少行号导致定位慢”。
- 只允许 Agent 围绕这个假设补最小实现和最小测试。
- 验证后写清假设是否成立；若不成立，下一轮先修假设，不继续扩大功能。
```

**坑**：

- 把“我想让 Agent 帮忙”误写成人类假设；假设必须说明可能原因、改动边界和验证信号。
- 假设写得太大，例如“提升项目质量”“优化架构”；短节拍中应压到一个文件、一个失败输出或一个可复核行为。
- Agent 给出更大的方案后，忘记回到原假设做取舍，导致练习目标被替换。
- 验证通过后只记录命令，不记录自己学到的判断规则；这样下一次仍然依赖 Agent 重新发现。
- 验证失败时继续让 Agent 猜第二版，而不是先解释失败如何推翻或修正了原假设。

**检查**：开始前能看到一条可证伪的 `Human hypothesis before agent`；结束时能看到假设与验证输出的对照，以及一句“下次我会先自己判断什么”。如果这三项缺一项，这轮更像代写任务，而不是刻意练习。
