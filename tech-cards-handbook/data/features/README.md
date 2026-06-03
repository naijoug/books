# ByteBite 结构化特性数据

这里存放可被 ByteBite 构建脚本消费的跨语言特性数据。

维护规则：

- 每个文件代表一个跨语言 feature，文件名与 `id` 保持一致。
- `coverage.required` 表示这个 feature 首批必须同步覆盖的语言。
- required 语言必须有 `status: ready` 的 implementation；如果确实不适用，写入 `coverage.notApplicable` 并说明原因。
- 只有 `status: ready` 的 implementation 会导出到 `bytebite/src/data/idioms.json`。
- `sourceCard` 可指向 `chapters/<language>/<card>.md`，用于追踪对应手册卡片。
- ByteBite 构建前会运行 `npm run sync:tech-cards`，从这些 YAML 生成/覆盖同 ID 的网站数据；尚未迁移到这里的旧 ByteBite idiom 会被暂时保留。
