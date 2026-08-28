# 解析层测试梯先于 Protected Mock

**问题**：Agent 看到 crawler、parser、adapter 这类链路缺测试时，常会直接去测最里面的 protected 方法：mock 网络、mock DOM、mock repository，再断言内部方法被调用。这样的测试很容易变成“mock 证明 mock”，既不能防真实回归，也会让下一轮不知道该从哪层继续。怎样在进入 protected mock 之前，先找到更稳定、低风险、可交接的测试层？

**要点**：

- 先把链路写成 5 层以内的边界图，例如 `config -> factory -> scheduler -> parser utility -> controller`；没有风险句的层先不测。
- 优先级从外到内：配置/schema、工厂分发、调度聚合、解析纯函数、薄 controller；只有这些层都不能覆盖风险时，才考虑 protected parser 或真实网络测试。
- 每轮只接一层，新增一个测试文件或一个紧密测试块；验证保留“formatter -> 聚焦测试 -> 类型/静态检查 -> 全量测试 -> diff check”的证据链。
- Mock 只停在依赖边界：repository 避免真实 DB，factory 避免调度器触网，scheduler/service 避免 controller 触发后台任务；不要 mock 被测对象自己的内部方法。
- 如果测试需要 sleep、固定执行顺序、私有字段、class 名或 protected 方法绕行才能断言，就先写 `Decision: Narrow`，回到纯函数或更外层公开契约。
- notebook / PR 交接写清：本轮选择哪一层、要防哪类回归、哪些层有意跳过、下一条最安全测试是什么；不要只写“补了 crawler 测试”。

**示例**：

```text
Observation:
一个新闻抓取链路包含平台配置导入、crawler type 分发、调度器并发执行、HTML/JSON 解析工具和 API controller。上一轮想直接测 StaticCrawler 的 protected parser，但需要 mock axios、cheerio、repository 和内部方法。

Human hypothesis before agent:
如果先覆盖 config/factory/scheduler/parser utility/controller 的公开边界，就能证明真实链路风险；若这些都已绿，再判断 protected parser 是否仍有独立价值。

Change slices:
1. config：mock repository + 临时配置文件，断言无效平台带 id 和 validator 细节。
2. factory：构造最小平台配置，断言 static/dynamic/api type 分发和 unknown type 诊断错误。
3. scheduler：mock crawler.crawl()，断言单平台失败不拖垮整批、重入被拒绝。
4. parser utility：直接喂 HTML、JSON、URL、日期、数字样本，断言纯函数规则。
5. controller：mock scheduler，断言 409、next(error) 和状态响应。

Verification handoff:
Focused proof: npm test --workspace=backend -- dataExtractor => 8 passed
Full proof: npm run type-check && npm run lint && npm test => all green
Skipped layers: StaticCrawler protected parser 暂不测；如果后续发现公开 crawl contract 无法定位解析规则，再单独开一轮。
Next safe test: 先审查 parser utility 是否缺业务样本，而不是继续 mock protected 方法。
```

**坑**：

- **从最深层开始**：protected parser 看似精准，实际常把输入、调度、存储和错误语义都 mock 掉。
- **一轮补完整条链**：一个提交同时改 config、factory、scheduler 和 parser，失败时无法判断是哪层契约破了。
- **controller happy path 重复集成测试**：薄层测试只补 409、错误转发、状态语义等未覆盖边界；不要重复测 integration 已覆盖的成功响应。
- **把 class 名当契约**：断言具体实现名可能只是测试实现细节；优先断言公开行为、错误语义和统计字段。
- **验证证据不可移植**：报告里只写“测试通过”，没有聚焦命令、全量命令和 changed paths，下一轮无法复查。

**检查**：提交前逐条问：是否先画出链路和风险句；是否只接一层；mock 是否停在依赖边界而不是被测对象内部；是否有聚焦与全量验证输出；是否写清跳过 protected mock 的理由和下一条安全测试。任一项缺失，就先收窄测试层级，不要继续堆 mock。
