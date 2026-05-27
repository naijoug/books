# Flutter 测试先覆盖核心交互路径

**问题**：Flutter UI 变化快，测试应该从哪里开始？

**要点**：

- 先测核心交互：登录、下单、保存、搜索。
- Widget 测试覆盖 UI 状态变化。
- 端到端测试数量少但覆盖关键路径。

**示例**：

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class Counter extends StatefulWidget {
  const Counter({super.key});

  @override
  State<Counter> createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  var count = 0;

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: () => setState(() => count += 1),
      child: Text('$count'),
    );
  }
}

void main() {
  testWidgets('counter increments', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: Counter()));

    expect(find.text('0'), findsOneWidget);
    await tester.tap(find.byType(TextButton));
    await tester.pump();
    expect(find.text('1'), findsOneWidget);
  });
}
```

最小验证方式：把示例保存为 `test/counter_test.dart`，运行 `flutter test test/counter_test.dart`，确保按钮点击后断言从 `0` 变为 `1`。

**坑**：只做快照测试很容易验证到“长得像”，但没验证用户能不能完成任务；示例必须包含被测 widget，否则读者无法直接判断测试在验证什么。

**检查**：如果核心按钮失效，测试是否会失败？示例是否能复制到最小 Flutter 工程中直接运行？
