# 双角色 E2E Helper 固定入口与权限契约

## 问题

同一条真实入口常常要覆盖多个角色和多个 viewport：desktop 点侧边栏 profile，mobile 点 role pill；学生进入后只能读，家长进入后可以保存。最初直接复制三份 Playwright 用例最快，但当锚点、按钮文案或移动端入口改变时，重复断言会一起漂移，下一轮只知道“很多测试红了”，不知道是入口坏、滚动目标坏，还是权限语义坏。

这张卡解决的问题是：在已有真实 E2E 路径通过后，如何把重复点击和重复断言收束成 helper，同时保留角色契约的可读性。

## 要点

- 先证明真实路径，再抽 helper；不要用 helper 抽象替代第一次 E2E 证明。
- 把 helper 拆成两类：动作 helper 只负责“怎么进入目标区域”，断言 helper 只负责“该角色在目标区域应看到什么”。
- 调用处仍要读得出业务意图，例如 `readonly: true`、`mode: "editable"` 或 `role: "parent"`，不要把学生/家长语义藏进 helper 内部默认值。
- 同一 helper 要覆盖 viewport 差异，但不要把角色切换、入口点击、区域定位和权限断言塞进一个黑盒函数。
- helper 化之后仍要跑覆盖所有 viewport project 的聚焦 E2E，再跑相关单元测试、类型检查、构建和 diff check，确认只是测试结构收束而不是语义降级。

适用信号通常是：同一目标 section 已经被 3 个以上用例重复定位；desktop/mobile 入口选择器不同但业务语义相同；角色差异集中在“只读提示 / 保存按钮 / 权限文案”这类可参数化断言上。

## 示例

把入口动作和目标区域断言分开：

```js
async function openProfileShortcut(page, projectName) {
  if (projectName === "mobile") {
    await page.getByRole("button", { name: /学生|家长/ }).click();
    return;
  }

  await page.locator(".sidebar-profile").click();
}

async function expectLearningProfileSection(page, options = {}) {
  const { readonly = false } = options;
  const section = page.locator("#learning-profile-settings");

  await expect(section).toBeInViewport();

  if (readonly) {
    await expect(section).toContainText("当前页面不会保存学习资料变更");
    await expect(section.getByRole("button", { name: "保存学习资料" })).toHaveCount(0);
    return;
  }

  await expect(section).not.toContainText("当前页面不会保存学习资料变更");
  await expect(section.getByRole("button", { name: "保存学习资料" })).toBeEnabled();
}
```

用例保留业务语言，而不是保留选择器细节：

```js
test("student profile shortcut opens readonly learning-profile settings", async ({ page }, testInfo) => {
  await openProfileShortcut(page, testInfo.project.name);
  await expectLearningProfileSection(page, { readonly: true });
});

test("parent profile shortcut opens editable learning-profile settings", async ({ page }, testInfo) => {
  await page.getByRole("button", { name: "家长视角" }).click();
  await openProfileShortcut(page, testInfo.project.name);
  await expectLearningProfileSection(page, { readonly: false });
});
```

如果失败发生在 `openProfileShortcut`，优先怀疑入口选择器或导航；如果失败发生在 `expectLearningProfileSection`，优先怀疑锚点、viewport 或权限契约。职责拆开后，helper 不会吞掉调试方向。

## 坑

- **先抽象后证明**：还没有一条真实路径通过时就抽 helper，会把“路径是否真的能走通”藏成实现细节。
- **万能 helper**：`setupAndAssertProfileSettings()` 同时登录、切角色、点击、等待、断言，会让失败定位比重复代码更差。
- **布尔值失语**：`true/false` 调用太多时，读者看不出代表只读还是可编辑；必要时改成 `{ mode: "readonly" }`。
- **只抽动作不抽断言**：入口选择器统一了，但锚点、只读提示、保存按钮仍散落在多个用例里，后续漂移照样多点爆炸。
- **只跑单 viewport**：helper 里有 desktop/mobile 分支时，聚焦 E2E 必须覆盖所有 Playwright project，否则另一条入口分支可能静默坏掉。

## 检查

提交前按这个顺序核对：

1. 是否已有至少一条真实 E2E 路径先证明入口、滚动目标和角色预期？
2. 动作 helper 名字是否只表达用户动作，断言 helper 名字是否只表达目标区域契约？
3. 调用处是否仍能一眼看出覆盖的角色和权限状态？
4. 聚焦 E2E 是否覆盖 desktop/mobile 等所有 viewport project，并给出 passed count？
5. 是否复跑相关单元测试、类型检查、构建和 `git diff --check -- <owned e2e file>`？
6. notebook 或交接记录是否写清：`helperized action`、`helperized assertion`、`covered roles`、`covered projects`、`still separate`？

一句话判断：入口变动只需要改动作 helper，权限语义变动只需要改断言 helper；如果两者仍然互相牵连，说明 helper 边界还没有拆对。
