# 规格抽屉 E2E 要锁决策字段

## 问题

开发工作台里的规格抽屉经常不只是说明文案，而是下一轮实现的交接面板：素材需求、平台 readiness、开放缺口、来源文档都会决定能否继续开发、测试或发布。

如果 E2E 只验证主预览能打开，团队会得到一个漂亮 demo，却不知道音频是否授权、小程序是否实现、哪些题型仍缺素材。下一轮 Agent 或开发者只能重新读设计文档，甚至误把“可预览”当成“可上线”。

这张卡解决的问题是：如何把规格抽屉写成可复判的 E2E 验收契约，让测试失败能指出缺失的决策字段，而不是只证明页面容器存在。

## 要点

- 先选一个最能代表风险的样本：素材依赖多、平台状态不全、开放缺口明确；不要一开始参数化全部题型。
- 至少覆盖五类字段：规格身份、素材需求、平台 readiness、开放缺口、来源文档。
- 断言要落在抽屉区域内，避免主预览或页面其他位置的同名文案让测试误绿。
- 平台状态要分开断言，例如 Web partial 和小程序 not-implemented 是两条不同后续动作。
- 来源文档路径必须可见；否则测试只能证明当前 fixture 文案存在，不能帮助接手者回到设计依据。
- 多 Playwright config 的仓库要显式使用 lab config，并在交接里写清 passed count、未覆盖样本和下一条安全切片。

适用信号通常是：页面是审查/开发工作台；主预览已能渲染但上线仍依赖素材、授权或平台适配；抽屉里已有 `media`、`readiness`、`open gaps`、`source doc` 等字段；失败时需要告诉接手者“还缺什么”，而不是只留截图。

## 示例

先把抽屉区域定位为一个明确的审查面板，再在面板内断言决策字段：

```js
test("surfaces media requirements and open gaps in the spec drawer", async ({ page }) => {
  await page.goto("/activity-lab.html?id=des-listen-picture-default");
  await expect(page.locator('[data-testid="activity-lab-root"]')).toBeVisible();

  const specDrawer = page.getByRole("complementary", {
    name: "设计规格与审查面板",
  });

  await expect(specDrawer.getByRole("heading", { name: "设计规格卡 (Spec Details)" })).toBeVisible();
  await expect(specDrawer.getByText("des-listen-picture-default")).toBeVisible();
  await expect(specDrawer.getByText("音频: stimulus-required")).toBeVisible();
  await expect(specDrawer.getByText("图像: required")).toBeVisible();
  await expect(specDrawer.getByText("Web: partial")).toBeVisible();
  await expect(specDrawer.getByText("小程序: not-implemented")).toBeVisible();
  await expect(specDrawer.getByText("正版课本听力录音未授权接入")).toBeVisible();
  await expect(
    specDrawer.getByText("docs/design/learning-activities/english/listen-and-choose-picture.md"),
  ).toBeVisible();
});
```

交接记录不要只写“E2E added”，而要写出字段覆盖范围：

```text
Spec drawer contract added: des-listen-picture-default
Fields covered: identity / media / platform readiness / open gaps / source doc
Proof: pnpm exec playwright test ... --config playwright.activity-lab.config.mjs (2 passed)
Not covered yet: second sample with implemented mini-program path
Next safe slice: extract drawer assertion helper after the second sample repeats the same field shape
```

## 坑

- **只测抽屉打开**：`complementary` 可见只能证明容器存在，不能证明素材、平台和缺口信息完整。
- **字段断言散在全页**：全页 `getByText` 可能吃到主预览或隐藏 fixture 文案；应把断言限制在抽屉区域。
- **平台状态合并成一句话**：`Web partial / 小程序 not-implemented` 被合并后，下一轮无法判断先补哪个平台。
- **缺口只写在 fixture 名称里**：`listen-picture` 不能替代“正版听力录音未授权接入”这样的可执行缺口。
- **过早抽 helper**：第一个样本还没证明字段形状时就抽通用 helper，会把真正的验收标准藏进抽象里。
- **默认 runner 误绿或误红**：多 config 仓库中默认 Playwright runner 可能找不到 lab 测试；命令必须显式写出 config。

## 检查

提交前按这个顺序核对：

1. 本轮样本是否代表最高交接风险，而不是随机选了最容易通过的题型？
2. 抽屉断言是否覆盖 identity、media、readiness、open gaps、source doc 五类字段？
3. 所有字段断言是否限制在规格抽屉区域内？
4. readiness 是否按平台拆开，且每个平台状态都能导出下一步动作？
5. 交接记录是否写清 proof command、passed count、未覆盖样本和下一条安全切片？
6. 如果准备抽 helper，是否已经有第二个样本复用了同一字段形状？

一句话判断：规格抽屉 E2E 的目标不是锁死每个展示文案，而是锁住“谁能继续做下一块、还缺什么证据、哪个平台未完成”的决策字段；如果测试失败不能回答这些问题，它就还只是 UI 存在性测试。
