# DOM 测试环境前先锁 Helper 契约，不要为一个窄副作用扩大依赖面

## 问题

前端改动只差一个真实 DOM 环境就能验证时，Agent 很容易在短节拍任务里直接引入 `jsdom`、Testing Library 或 Playwright；也可能反过来只写静态断言，把“点击后滚动到学习资料区”这类行为当作已经证明。

更稳的中间层是：先把浏览器副作用抽成一个很窄的 helper，用现有 Node/Vitest 环境锁住目标、参数和空目标行为；再把“真实 DOM 交互仍未覆盖”显式交接给下一段。

## 要点

- **先识别副作用是否足够窄**：适合抽 helper 的行为通常是 `getElementById(...).scrollIntoView(...)`、`history.pushState(...)`、`localStorage.setItem(...)`、analytics event 组装这类“选择目标 + 调用浏览器 API”。
- **把浏览器对象变成可注入接口**：默认使用真实 `document` / `window`，测试传入只包含所需方法的 fake object，避免为了一个契约改测试栈。
- **测试契约，不冒充端到端证明**：窄测试只证明 id、参数、空目标不抛错和调用顺序；不要声称它证明了可见位置、focus、布局或用户点击路径。
- **验证梯要补到 build/check**：helper 单测通过后，还要跑组件既有测试、TypeScript check、build 和 path-scoped diff check，确认抽象没有破坏真实包。
- **交接未验证项**：最终记录要写清 `Still unproven: DOM unit / Playwright / manual visual QA`，让下一轮知道下一步是升级证明，而不是继续扩 helper。

## 示例

不要只在 effect 里内联浏览器调用：

```ts
useEffect(() => {
  if (!curriculumAnchor) return;
  document
    .getElementById("learning-profile-settings")
    ?.scrollIntoView({ behavior: "smooth", block: "start" });
}, [curriculumAnchor]);
```

可以先抽成窄 helper：

```ts
export const SETTINGS_CURRICULUM_SECTION_ID = "learning-profile-settings";

export function scrollToSettingsCurriculumSection(
  ownerDocument: Pick<Document, "getElementById"> = document,
) {
  ownerDocument
    .getElementById(SETTINGS_CURRICULUM_SECTION_ID)
    ?.scrollIntoView({ behavior: "smooth", block: "start" });
}
```

测试只伪造必须接口：

```ts
it("scrolls to the stable curriculum section", () => {
  const calls: ScrollIntoViewOptions[] = [];
  const ownerDocument = {
    getElementById(id: string) {
      expect(id).toBe(SETTINGS_CURRICULUM_SECTION_ID);
      return {
        scrollIntoView(options?: boolean | ScrollIntoViewOptions) {
          calls.push(options as ScrollIntoViewOptions);
        },
      } as HTMLElement;
    },
  } satisfies Pick<Document, "getElementById">;

  scrollToSettingsCurriculumSection(ownerDocument);

  expect(calls).toEqual([{ behavior: "smooth", block: "start" }]);
});
```

这时最终报告应写成：

```text
Helper contract fixed: scrollToSettingsCurriculumSection -> learning-profile-settings / smooth start
Narrow proof: vitest target file passed
Still unproven: real avatar click -> settings page -> visual scroll position
Next upgrade: DOM unit or Playwright path test
```

## 坑

- 为一个滚动参数引入大测试栈，导致 lockfile、测试配置和 CI 时间成为本轮主要风险。
- 只验证 helper 被调用，却没有断言目标 id 和 `scrollIntoView` 参数。
- helper 单测通过后，报告写成“用户路径已验证”，但没有真实 DOM、点击入口、focus 或布局证据。
- 抽 helper 时把 `document` 直接读到模块顶层，导致 SSR、Node test 或 build 阶段报错。
- 测试只覆盖目标存在的 happy path，没有覆盖目标缺失时不抛错。

## 检查

提交前问自己：这个行为是否只是“选择目标 + 调 API”？helper 是否把浏览器对象收窄成可注入接口？测试是否会在 id 拼错、参数漂移或目标缺失处理错误时失败？是否跑过组件既有测试、TypeScript check、build 和 `git diff --check -- <owned paths>`？最终 notebook 是否明确写出 DOM/E2E 仍未覆盖的下一步？
