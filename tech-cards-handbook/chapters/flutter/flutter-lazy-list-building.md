# Flutter 列表必须按需构建

**问题**：长列表为什么会卡？

**要点**：

- 大量列表项使用 `ListView.builder`。
- item 要尽量小，避免在 build 中做重计算。
- 网络图片、复杂布局和阴影都可能影响滚动性能。

**示例**：

```dart
ListView.builder(
  itemCount: messages.length,
  itemBuilder: (context, index) {
    final message = messages[index];
    return ListTile(
      title: Text(message.title),
      subtitle: Text(message.preview),
    );
  },
)
```

**坑**：`Column(children: items.map(...).toList())` 会一次性构建所有子项，不适合长列表。

**检查**：列表数据超过几十项时，是否仍然按需创建可见项？
