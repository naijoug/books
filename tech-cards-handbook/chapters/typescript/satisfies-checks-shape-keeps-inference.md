# `satisfies` 检查形状但保留推断

**问题**：如何检查一个对象符合接口，同时又保留字面量类型和具体 key？

**要点**：

- 类型注解会把值拓宽到声明的接口形状。
- `satisfies` 只检查值是否满足目标类型，不会把变量本身改成目标类型。
- 适合配置表、路由表、权限表等“既要约束结构，又要保留精确信息”的场景。

**示例**：

```typescript
type RouteConfig = Record<string, {
  path: string;
  requiresAuth: boolean;
}>;

const routes = {
  home: { path: "/", requiresAuth: false },
  dashboard: { path: "/dashboard", requiresAuth: true },
} satisfies RouteConfig;

// key 仍然是 "home" | "dashboard"，不是宽泛的 string
type RouteName = keyof typeof routes;

function navigateTo(name: RouteName) {
  return routes[name].path;
}

navigateTo("dashboard");
// navigateTo("settings"); // 编译错误
```

**坑**：`satisfies` 不会改变运行时数据，也不会让不可信 JSON 自动安全。外部输入仍然需要运行时校验。

**检查**：如果你既想发现结构错误，又想继续使用具体 key、字面量值或更窄的推断类型，优先考虑 `satisfies`，不要直接把变量标成宽泛接口。
