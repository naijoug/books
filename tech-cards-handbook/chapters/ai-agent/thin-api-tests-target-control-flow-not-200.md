# 薄 API 测试先锁控制流，不重复 200

**问题**：Agent 给 controller、route handler、middleware 补测试时，最容易写出一排“mock service -> 返回 200 -> 断言 body”的单测；这些 happy path 往往已经被 integration test 覆盖，新增单测只是在证明 mock 会返回 mock。薄 API 层到底该测什么，才能防真实回归而不是堆覆盖率？

**要点**：

- 写薄层单测前先读已有 request-level / integration 测试，列出“已经证明的 200 路径”和“仍未证明的控制流语义”。
- 优先补会改变控制流或错误语义的分支：`409` 重入短路、`304` cache hit、`headersSent` 后不重复响应、空 body / 非法 id / 枚举错误、`404` / `409`、`next(error)`、结构化失败 payload。
- 参数传递只在薄层有业务转换时才测，例如 `enabledOnly`、分页、过滤条件、排序映射；如果只是原样转发且 integration 已覆盖响应，就停止。
- Mock 只停在薄层外部依赖：controller 可以 mock repository/service/scheduler，middleware 可以 mock request/response/next；不要 mock 被测 handler 自己的 helper 再断言 helper 被调用。
- 一轮只补一个薄边界或一类相邻 middleware，验证保留 `formatter -> focused test -> type/lint -> full test -> diff check`，并在交接写清“为什么不是重复 200”。
- 当新增测试只剩多个成功响应样本时，写 `Decision: Stop`，转向 integration 风险、底层纯函数，或把本轮取舍沉淀为文档。

**示例**：

```text
Observation:
已有 api.test.ts 覆盖 GET /platforms 的成功响应；PlatformController 仍未直接证明重复 id、missing platform、无效 config、crawler 试跑失败和 repository reject 的语义。

Thin boundary test plan:
- createPlatform: invalid config => 400 且不调用 create；duplicate id => 409。
- updatePlatform: missing => 404；invalid crawler config => 400。
- testPlatform: crawler 公开方法失败 => 返回 success:false + error，而不是 next(error)。
- getPlatforms: enabledOnly=true 被传给 repository。
- repository reject: 调用 next(error)，不伪造成功响应。

Verification handoff:
Focused proof: npm test --workspace=backend -- platformController => 14 passed
Full proof: npm run type-check && npm run lint && npm test => all green
Stop condition: NewsController 若只剩 200 查询 happy path，不再补薄层单测；先找 integration 未覆盖的错误转发或参数转换。
```

**坑**：

- **重复 integration happy path**：如果 request-level 测试已经证明 200 响应，薄层单测再断言一次同样 body，价值很低。
- **把 mock 当业务证据**：mock repository 返回什么，controller 就返回什么；除非断言的是状态码、短路、错误转发或参数转换，否则只是 mock 回声。
- **漏掉“不调用下游”**：短路分支的关键不是返回 `409` / `304`，而是没有启动任务、没有写库、没有继续 `json()`。
- **过度合并边界**：一个测试同时 mock scheduler、repository、factory、HTTP client 和 clock，通常说明它已经不是薄 API 测试；收窄到 service 或纯函数。
- **失败不改变计划**：聚焦测试失败后只改断言让它变绿，却不记录失败暴露的是 fixture、接口契约还是目标层级选择问题。

**检查**：提交前逐条确认：是否读过 integration 覆盖；新增 case 是否至少命中一种控制流或错误语义；短路是否断言“不调用下游”；mock 是否只在外部依赖边界；交接是否写清 focused/full proof 和停止条件。若答不出来，就删掉重复 200 case，先补更有诊断价值的分支。
