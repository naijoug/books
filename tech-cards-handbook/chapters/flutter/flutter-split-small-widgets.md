# Flutter 小组件拆分比大 build 更重要

**问题**：为什么一个页面 build 方法越来越难维护？

**要点**：

- 不需要状态的部分优先抽成 `StatelessWidget`。
- 重复 UI 抽组件，不要只抽函数返回 widget。
- `const` widget 能减少不必要重建。

**示例**：

```dart
class TitleText extends StatelessWidget {
  const TitleText({super.key, required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Text(text, style: Theme.of(context).textTheme.titleLarge);
  }
}
```

**坑**：把所有 UI 都堆在一个 `build` 方法里，会让状态、布局和交互纠缠在一起。

**检查**：一个 build 方法是否已经需要滚动很久才能看完？是的话先拆组件。
