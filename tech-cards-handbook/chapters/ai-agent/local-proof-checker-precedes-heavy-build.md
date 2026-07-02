# 本地 proof checker 先于重型构建，不要把每次小改都交给全量 build

**问题**：Agent 在文档、配置或索引做小改动时，如何快速证明“本轮没有引入基础破损”，同时避免每次都用耗时的全量构建当第一道反馈？

**要点**：

- 把 proof checker 定义成“窄范围、可重复、能失败”的 preflight，而不是万能 linter：它只覆盖本轮最容易出错的基础契约。
- 先检查文件存在、相对链接、frontmatter、绝对路径、include 目标这类低成本事实；主题渲染、插件行为、锚点完整性仍交给全量 build。
- checker 必须对“目标不存在”“匹配 0 个文件”“链接目标只是目录而非文件”这类情况失败，不能输出假绿灯。
- 每次扩规则都要由真实误报或漏报驱动，并补最小 fixture；不要因为还能想到规则就继续膨胀。
- 最终报告同时写 proof checker 和全量 build 的边界：前者证明基础契约，后者证明集成渲染。

**示例**：

```text
改动场景：
- 在 docs 的 AI 目录页新增一条跨目录链接，指向 scripts/check-markdown-proof.py。

本地 proof checker：
- 输入：本轮改动的 2-3 个 Markdown 文件。
- 检查：frontmatter title、相对链接是否解析到文件、是否包含本机用户目录绝对路径、VuePress include 文件目标是否存在。
- 失败：如果链接指向不存在的脚本，立即报 broken local link。

全量 build：
- 在 proof checker 通过后运行 VuePress build。
- 只用它确认侧边栏、插件、页面渲染和未覆盖的集成行为。
```

一个可接力的执行顺序：

```text
1. 改前：对即将修改的文件运行 proof checker，确认基线为绿。
2. 修改：只改本轮明确接管的路径。
3. 改后：对同一组文件运行 proof checker。
4. 若 checker 失败：先修本轮改动；若是 checker 漏报/误报，补最小 fixture 后再改实现。
5. 若 checker 通过：再按需要运行全量 build，并在 notebook 写清两类验证各自证明了什么。
```

**坑**：

- 把 checker 写成“扫描到 0 个文件也成功”，导致路径拼错时假通过。
- 一次性把锚点、sidebar、插件、代码块执行、外链可达性都塞进 checker，最后维护成本超过全量 build。
- checker 失败后只改最终描述，不让失败改变顺序或范围。
- 只报告“构建通过”，不说明轻量 preflight 覆盖了哪些本轮风险，下一轮无法判断是否可复用。
- 用绝对路径写入文档或 notebook，让 proof 只能在当前机器成立。

**检查**：一次小改至少能回答三件事：proof checker 是否在改前和改后都运行过；它覆盖的契约是否和本轮风险匹配；全量 build 是否只承担 checker 不该承担的集成验证。如果 checker 新增了规则，必须能指向一个真实失败样例或最小回归 fixture。
