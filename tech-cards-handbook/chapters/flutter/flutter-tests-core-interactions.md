# Flutter 测试先覆盖核心交互路径

**问题**：Flutter UI 变化快，测试应该从哪里开始？

**要点**：

- 先测核心交互：登录、下单、保存、搜索。
- Widget 测试覆盖 UI 状态变化。
- 端到端测试数量少但覆盖关键路径。

**示例**：

```dart
testWidgets('counter increments', (tester) async {
  await tester.pumpWidget(const MaterialApp(home: Counter()));

  expect(find.text('0'), findsOneWidget);
  await tester.tap(find.byType(TextButton));
  await tester.pump();
  expect(find.text('1'), findsOneWidget);
});
```

**坑**：只做快照测试很容易验证到“长得像”，但没验证用户能不能完成任务。

**检查**：如果核心按钮失效，测试是否会失败？
