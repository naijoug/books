# Flutter 导航要区分页面结果和全局状态

**问题**：页面返回时如何把选择结果传回来？

**要点**：

- 一次性页面结果通过 `Navigator.pop(result)` 返回。
- 全局登录态、购物车、主题不要靠路由结果传递。
- 路由参数保持小而明确。

**示例**：

```dart
final selected = await Navigator.push<String>(
  context,
  MaterialPageRoute(builder: (_) => const CityPickerPage()),
);

if (selected != null) {
  setState(() => city = selected);
}
```

**坑**：把复杂对象在多级页面间来回传，容易造成状态来源不清。

**检查**：这个数据是“页面选择结果”，还是“应用共享状态”？
