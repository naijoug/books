# Flutter 基础布局先理解 Row、Column、Container

**问题**：Flutter 页面为什么经常溢出或对不齐？

**要点**：

- `Row` 横向排列，`Column` 纵向排列。
- 主轴由排列方向决定，交叉轴垂直于主轴。
- `Container` 常用于尺寸、背景、边框和内边距组合。

**示例**：

```dart
Row(
  mainAxisAlignment: MainAxisAlignment.center,
  children: const [
    Icon(Icons.star),
    SizedBox(width: 8),
    Text('Star'),
  ],
)
```

**坑**：`Row` 里的长文本不加 `Expanded` 容易溢出。

**检查**：每个横向布局里的可伸缩元素是否明确包了 `Expanded` 或设置了约束？
