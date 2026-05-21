# Flutter 异步回调后先检查 `mounted`

## 问题

页面发起异步请求、等待弹窗结果或延迟执行任务后，用户可能已经离开页面。此时回调继续调用 `setState`、读取 `context` 或弹 `SnackBar`，容易遇到异常：

```text
setState() called after dispose()
```

这类问题通常不是请求本身错了，而是异步结果回来时 `State` 已经不在组件树里。

## 要点

- `State.mounted` 表示这个 `State` 是否仍挂在组件树上；`dispose` 后会变成 `false`。
- `await` 之后再更新 UI 前，先判断 `if (!mounted) return;`。
- 检查应放在每个可能跨越时间的边界后：网络请求、文件选择、权限弹窗、`showDialog`、`Future.delayed`。
- `mounted` 只能避免已销毁页面更新 UI；它不替代取消请求、错误处理或业务状态管理。

## 示例

在异步加载后更新页面状态：

```dart
class UserPage extends StatefulWidget {
  const UserPage({super.key, required this.api});

  final UserApi api;

  @override
  State<UserPage> createState() => _UserPageState();
}

class _UserPageState extends State<UserPage> {
  User? _user;
  Object? _error;
  bool _loading = false;

  Future<void> _loadUser() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final user = await widget.api.fetchCurrentUser();
      if (!mounted) return;

      setState(() {
        _user = user;
        _loading = false;
      });
    } catch (error) {
      if (!mounted) return;

      setState(() {
        _error = error;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return ErrorView(error: _error!, onRetry: _loadUser);
    }

    final user = _user;
    if (user == null) {
      return EmptyView(onRefresh: _loadUser);
    }

    return UserCard(user: user);
  }
}
```

异步弹窗后使用 `context` 也要检查：

```dart
Future<void> _confirmDelete() async {
  final confirmed = await showDialog<bool>(
    context: context,
    builder: (context) => const DeleteConfirmDialog(),
  );

  if (!mounted || confirmed != true) return;

  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(content: Text('Deleted')),
  );
}
```

## 坑

- 只在 `try` 成功分支检查 `mounted`，但在 `catch` 里仍然 `setState`。
- 把 `mounted` 检查放在 `await` 之前；真正需要保护的是 `await` 之后的 UI 操作。
- 误以为 `mounted` 会取消网络请求；请求仍会完成，只是结果不再写回已销毁页面。
- 在工具类或 repository 里依赖 `BuildContext` 和 `mounted`，导致 UI 生命周期泄漏到数据层。

## 检查

- 搜索 `await` 后紧跟的 `setState`、`Navigator`、`ScaffoldMessenger`、`showDialog` 回调，确认中间有 `mounted` 检查。
- 快速进入页面后立刻返回，异步请求完成时不应出现 `setState() called after dispose()`。
- 成功和失败分支都要有同样的生命周期保护。
- 如果需要真正中断耗时任务，应另行设计取消机制，而不是只依赖 `mounted`。
