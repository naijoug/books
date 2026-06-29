# 技术卡片随身宝典:技术栈索引

正式内容按技术栈分目录维护;每张卡片是一个独立 Markdown 文件。

## 阅读方式

1. 先进入对应技术栈目录。
2. 按目录 README 的列表顺序阅读。
3. 遇到具体问题时,直接打开对应卡片。

## 技术栈目录

| 技术栈 | 目录 | 卡片数 |
|---|---|---|
| Python 技术卡片 | [`python/`](python/) | 23 |
| Go 技术卡片 | [`go/`](go/) | 18 |
| Rust 技术卡片 | [`rust/`](rust/) | 20 |
| TypeScript 技术卡片 | [`typescript/`](typescript/) | 31 |
| React 技术卡片 | [`react/`](react/) | 54 |
| Swift 技术卡片 | [`swift/`](swift/) | 14 |
| Flutter 技术卡片 | [`flutter/`](flutter/) | 14 |
| AI Agent 系统实践卡片 | [`ai-agent/`](ai-agent/) | 31 |

## 跨技术栈复盘路径

当一个问题已经在多个技术栈里反复出现,优先按"边界问题"而不是"语言特性"来复盘:

### 存储与 adapter 边界

这条路径适合审查 CRUD、后台管理、API handler 和 repository 代码,目标是防止外部契约、领域模型和数据库 row 相互泄漏。

1. **输入边界**:先读 Go 的 [`go/request-json-does-not-decode-into-database-row.md`](go/request-json-does-not-decode-into-database-row.md),确认请求 JSON 只进入 request DTO / command,不直接写进数据库 row。
2. **handler 输出边界**:再读 Go 的 [`go/http-handler-does-not-bind-database-model.md`](go/http-handler-does-not-bind-database-model.md) 和 [`go/http-handler-hides-internal-errors.md`](go/http-handler-hides-internal-errors.md),确认 handler 不透传存储字段、内部错误和日志上下文。
3. **领域类型边界**:切到 Rust 的 [`rust/newtype-separates-domain-from-primitive.md`](rust/newtype-separates-domain-from-primitive.md) 与 [`rust/from-into-do-not-skip-validation-boundary.md`](rust/from-into-do-not-skip-validation-boundary.md),检查 `UserId`、`EmailAddress`、状态枚举这类概念是否先经过可失败验证再进入业务层。
4. **repository 边界**:最后读 Rust 的 [`rust/repository-does-not-leak-database-row.md`](rust/repository-does-not-leak-database-row.md),确认 repository trait 只暴露领域模型和领域错误,ORM model / SQL row / driver error 被限制在 adapter 内。

复盘输出可以是一张四列表:`输入 DTO`、`领域 command/model`、`存储 row`、`输出 DTO`。如果任意一列的字段名、错误语义或类型直接复制到另一列,就要补 mapper、newtype 或显式错误转换。

### 存储边界审查清单

如果需要在代码审查中快速走查存储边界,可以直接使用 [`storage-boundary-review-checklist.md`](storage-boundary-review-checklist.md),它把输入 DTO、领域类型、可失败转换、repository adapter 和输出 DTO 压缩成五个检查点,并附带不符合项记录表。

### 错误传播与分类边界

这条路径适合审查 service、repository、handler 和 CLI command 的错误返回,目标是让错误既能保留诊断上下文,又能被调用方稳定分类处理。

1. **先确认失败是否进入类型系统**:读 Rust 的 [`rust/result-means-failable-with-reason.md`](rust/result-means-failable-with-reason.md),把"可能失败且有原因"写进返回类型,而不是用空值、布尔值或 panic 暗示。
2. **再确认上下文没有断链**:读 Go 的 [`go/errors-keep-context.md`](go/errors-keep-context.md),检查每一层是否用 `%w` 保留根因,并补上"做什么、对谁做"的上下文。
3. **再确认错误是否可分类**:读 Python 的 [`python/custom-exception-hierarchy-makes-errors-classifiable.md`](python/custom-exception-hierarchy-makes-errors-classifiable.md) 和 Go 的 [`go/error-wrapping-vs-result-propagation.md`](go/error-wrapping-vs-result-propagation.md),比较 Python 的 `isinstance`/`except` 子类、Go 的 `errors.Is`/`errors.As` 与 Rust 的 `From`/`?`/`match`,确认调用方能区分重试、降级、用户可见错误和内部故障。
4. **确认恢复动作显式化**:读 Python 的 [`python/retry-policy-explicit-not-hidden-loop.md`](python/retry-policy-explicit-not-hidden-loop.md)、Rust 的 [`rust/retry-strategy-explicit-not-implicit-loop.md`](rust/retry-strategy-explicit-not-implicit-loop.md)、Go 的 [`go/retry-policy-explicit-not-hidden-loop.md`](go/retry-policy-explicit-not-hidden-loop.md) 和 Flutter 的 [`flutter/flutter-retry-policy-explicit-not-hidden-loop.md`](flutter/flutter-retry-policy-explicit-not-hidden-loop.md),把"哪些错误可重试、最多重试几次、如何退避、耗尽后返回什么"从临时 `for` / `while` / `loop` / 嵌套 `match` / `if err != nil` / 按钮回调中拆成可测试的策略。
5. **确认降级决策在调用方**:读 Python 的 [`python/degradation-strategy-at-caller-not-callee.md`](python/degradation-strategy-at-caller-not-callee.md)、Rust 的 [`rust/degradation-strategy-at-caller-not-callee.md`](rust/degradation-strategy-at-caller-not-callee.md)、Go 的 [`go/degradation-strategy-at-caller-not-callee.md`](go/degradation-strategy-at-caller-not-callee.md)、TypeScript 的 [`typescript/degradation-strategy-at-caller-not-callee.md`](typescript/degradation-strategy-at-caller-not-callee.md)、Swift 的 [`swift/swift-degradation-strategy-at-caller-not-callee.md`](swift/swift-degradation-strategy-at-caller-not-callee.md) 和 Flutter 的 [`flutter/flutter-degradation-strategy-at-caller-not-callee.md`](flutter/flutter-degradation-strategy-at-caller-not-callee.md),确认被依赖服务不可用时,降级(返回缓存、默认值、简化响应)由调用方根据业务容忍度决定,而不是被调方静默返回假结果。
6. **最后确认对外错误码来自领域**:读 Python 的 [`python/external-error-codes-domain-defined-not-leaked.md`](python/external-error-codes-domain-defined-not-leaked.md)、Rust 的 [`rust/external-error-codes-domain-defined-not-leaked.md`](rust/external-error-codes-domain-defined-not-leaked.md)、Go 的 [`go/external-error-codes-domain-defined-not-leaked.md`](go/external-error-codes-domain-defined-not-leaked.md)、TypeScript 的 [`typescript/external-error-codes-domain-defined-not-leaked.md`](typescript/external-error-codes-domain-defined-not-leaked.md)、Swift 的 [`swift/swift-external-error-codes-domain-defined-not-leaked.md`](swift/swift-external-error-codes-domain-defined-not-leaked.md) 和 Flutter 的 [`flutter/flutter-external-error-codes-domain-defined-not-leaked.md`](flutter/flutter-external-error-codes-domain-defined-not-leaked.md),检查对外响应或 UI view model 的错误码是否由领域枚举/异常定义、底层 SQL state / 驱动类型名 / 平台异常 message 是否被 adapter 翻译成稳定的领域错误码。
7. **把恢复动作收束到一张表**:如果重试、降级、字段错误、登录跳转和安全错误分散在多个调用方,用 Swift 的 [`swift/swift-error-recovery-decision-table.md`](swift/swift-error-recovery-decision-table.md)、Flutter 的 [`flutter/flutter-error-recovery-decision-table.md`](flutter/flutter-error-recovery-decision-table.md) 或后端语言的决策表卡片把领域错误码、调用方动作和 UI / 响应契约对齐；移动端先用 Swift / Flutter 的调用方降级卡片确认缓存/默认值没有藏在 repository 里，再把可降级错误接入决策表。

复盘输出可以是一张五列表:`底层错误`、`领域错误`、`调用方动作`、`重试/降级策略`、`对外消息`。如果上层需要知道 SQL 状态码、文件系统错误码或第三方 SDK 类型才能决策,就要在 adapter 边界补领域错误转换;如果对外消息直接拼接底层错误字符串,就要拆出日志上下文和用户可见错误码;如果重试次数、退避间隔或可重试错误集合散落在错误处理分支里,就要抽成显式策略并补最小测试。Python 侧可以用 [`python/error-recovery-path-needs-one-decision-table.md`](python/error-recovery-path-needs-one-decision-table.md)、Go 侧可以用 [`go/error-recovery-path-needs-one-decision-table.md`](go/error-recovery-path-needs-one-decision-table.md)、Rust 侧可以用 [`rust/error-recovery-path-needs-one-decision-table.md`](rust/error-recovery-path-needs-one-decision-table.md)、TypeScript 侧可以用 [`typescript/error-recovery-path-needs-one-decision-table.md`](typescript/error-recovery-path-needs-one-decision-table.md)、Swift 侧可以用 [`swift/swift-error-recovery-decision-table.md`](swift/swift-error-recovery-decision-table.md)、Flutter 侧可以用 [`flutter/flutter-error-recovery-decision-table.md`](flutter/flutter-error-recovery-decision-table.md) 把分类、重试、降级和对外错误码收束到一张决策表。

### 错误边界审查清单

如果需要在代码审查中快速走查错误边界，优先把 [`error-boundary-review-checklist.md`](error-boundary-review-checklist.md) 当作错误恢复复盘入口：它把上述路径压缩为六个检查点，每个检查点附带深度阅读卡片链接、不符合项记录表和决策表证据列。先用它定位"类型系统、上下文、分类、重试、降级、对外错误码"哪一环断掉，再回到对应语言卡片补实现。

### 审查清单配套样本包

使用清单之后，可以用 [`../samples/ai-agent-sample-pack.md`](../samples/ai-agent-sample-pack.md) 里的错误边界 review agent 输入样例直接启动一次可复核的小范围审查，其中包含 agent prompt、错误决策表模板和 `NARROW_FIRST` 证据边界交接记录。

### AI Agent dirty workspace 心跳接力

如果问题不是某个语言或代码边界，而是“周期性唤醒的 Agent 要在已有 dirty workspace 里继续工作”，优先从 [`ai-agent/`](ai-agent/) 的快速路径进入，而不是直接翻完整 AI Agent 目录。

最短使用顺序：

1. 先把 [`../samples/ai-agent-dirty-workspace-one-pager.md`](../samples/ai-agent-dirty-workspace-one-pager.md) 贴给本轮 Agent，要求它先记录启动快照。
2. 再按 [`ai-agent/README.md`](ai-agent/README.md) 里的“快速路径：dirty workspace 心跳接力”阅读 12 个步骤：心跳、防漂移、启动快照、规划取舍、无人值守默认动作、失败输出吸收、未提交与 staged 归属、提交范围台账、dirty workspace 收尾、验证与未验证项交接、提交状态读回和最终报告边界。
3. 如果需要更完整的 prompt 和交接样例，再打开 [`../samples/ai-agent-sample-pack.md`](../samples/ai-agent-sample-pack.md) 的 dirty workspace 心跳交接输入样例。

这条路径的输出不是一篇总结，而是一份可接力记录：本轮实际推进了什么、哪些 dirty path 没有接管、验证命令是什么、项目和 notebook 分别提交到了哪个 commit。

## 卡片维护规则

- 新卡片放入对应技术栈目录,文件名使用英文 `kebab-case`,不要使用纯数字命名。
- 每张正式卡片必须包含"问题、要点、示例、坑、检查"。
- 长教程、原始素材和未定稿片段不要直接放入正式卡片;先提炼成单一问题。
- 目录优先按具体技术栈命名,避免使用"前端""移动端"这类领域混合桶。
- 跨技术栈内容优先放在主要实践场景所在目录,并在相关目录 README 中交叉引用。
- Agent 系统设计、工具、记忆和心跳工作流放入 `ai-agent/`;具体 SDK 或语言实现优先放入对应技术栈目录。

## Verifier 覆盖边界

`scripts/verify_all_cards.py --language ...` 覆盖有代码块 verifier 的语言章节：Go、Python、Rust、TypeScript、React、Swift 和 Flutter。AI Agent 章节是工作流/运行边界卡片，不纳入语言代码 verifier；维护 `ai-agent/` 时按下面的索引校验、链接校验和每张卡片“问题、要点、示例、坑、检查”五段人工复核执行。

## 索引校验

更新任一 `chapters/<tech-stack>/` 目录后，先用下面的仓库相对路径脚本重新统计正式卡片数，再同步更新 `README.md` 和本文件的目录表：

```bash
python3 - <<'PY'
from pathlib import Path
base = Path('chapters')
counts = {
    path.name: len([f for f in path.glob('*.md') if f.name != 'README.md'])
    for path in sorted(base.iterdir())
    if path.is_dir()
}
print('total', sum(counts.values()))
for name, count in counts.items():
    print(name, count)
PY
```

提交前还要确认 `README.md` 的“当前共 N 张正式卡片”和本文件“技术栈目录”表中的数字都来自同一次统计，避免只更新某个入口。

## 链接校验

更新任何跨技术栈引用、样本包链接或目录 README 链接后，提交前至少跑一次 Markdown 内部链接扫描，确保相对路径没有因为移动文件或跨目录引用而断掉：

```bash
python3 - <<'PY'
import re
from pathlib import Path

root = Path('.')
missing = []
for md in root.rglob('*.md'):
    text = md.read_text(encoding='utf-8')
    for match in re.finditer(r'\[[^\]]+\]\(([^)]+)\)', text):
        target = match.group(1).split('#', 1)[0]
        if not target or '://' in target or target.startswith('mailto:'):
            continue
        if target.startswith('<') and target.endswith('>'):
            target = target[1:-1]
        resolved = (md.parent / target).resolve()
        if not resolved.exists():
            missing.append((str(md), target))

if missing:
    for source, target in missing:
        print(f'MISSING {source} -> {target}')
    raise SystemExit(1)
print('missing_links 0')
PY
```

这条检查应和上面的“索引校验”一起运行：索引数字保证入口可信，链接扫描保证读者从任意卡片跳转时不会进入不存在的路径。
