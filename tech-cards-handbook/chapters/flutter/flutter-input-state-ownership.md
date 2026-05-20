# Flutter 输入控件要明确状态归属

**问题**：TextField 的输入值应该存在哪里？

**要点**：

- 简单输入可用 `onChanged` 更新局部 state。
- 需要读取、清空、校验时使用 `TextEditingController`。
- controller 需要在 `dispose` 中释放。

**示例**：

```dart
TextField(
  decoration: const InputDecoration(
    labelText: 'Name',
    prefixIcon: Icon(Icons.person),
    border: OutlineInputBorder(),
  ),
  onChanged: (value) {
    print(value);
  },
)
```

**坑**：在 `build` 里新建 controller 会导致输入状态丢失。

**检查**：输入状态是否有清晰 owner？controller 是否释放？
