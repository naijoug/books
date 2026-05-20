# Flutter `setState` 只适合局部简单状态

**问题**：什么时候 `setState` 够用，什么时候该引入状态管理？

**要点**：

- 单个 widget 内部的小状态，用 `setState`。
- 跨页面、跨模块共享状态，用明确的状态管理方案。
- 状态变化范围越小，UI 越稳定。

**示例**：

```dart
class Counter extends StatefulWidget {
  const Counter({super.key});

  @override
  State<Counter> createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int count = 0;

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: () => setState(() => count++),
      child: Text('$count'),
    );
  }
}
```

**坑**：把全局用户信息、主题、权限状态都塞进顶层 `setState`，会造成大范围重建和难以追踪的数据流。

**检查**：状态是否只被当前 widget 使用？是的话 `setState` 通常足够。
