# Flutter `FutureBuilder` 要传入稳定的 Future

## 问题

页面需要展示异步数据时，很多人会在 `build` 里直接调用接口：

```dart
FutureBuilder<User>(
  future: api.fetchUser(userId),
  builder: (context, snapshot) {
    // ...
  },
)
```

这看起来简洁，但只要父组件重建、主题变化、键盘弹出或 `setState` 触发，`build` 就可能再次执行，导致同一个请求被重复发起，页面在 loading/data 之间抖动。

## 要点

- `build` 应该描述 UI，不应该顺手创建一次性的异步副作用。
- `FutureBuilder.future` 应尽量来自稳定字段，例如在 `initState` 中创建并缓存。
- 当输入参数变化时，在 `didUpdateWidget` 中判断参数是否真的改变，再重新创建 `Future`。
- `snapshot.connectionState` 只描述当前 Future 的状态，不等于业务状态机；错误、空数据和加载态要分开处理。

## 示例

把 Future 缓存在 State 中：

```dart
class UserProfile extends StatefulWidget {
  const UserProfile({super.key, required this.userId, required this.api});

  final String userId;
  final UserApi api;

  @override
  State<UserProfile> createState() => _UserProfileState();
}

class _UserProfileState extends State<UserProfile> {
  late Future<User> _userFuture;

  @override
  void initState() {
    super.initState();
    _userFuture = widget.api.fetchUser(widget.userId);
  }

  @override
  void didUpdateWidget(covariant UserProfile oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (oldWidget.userId != widget.userId || oldWidget.api != widget.api) {
      _userFuture = widget.api.fetchUser(widget.userId);
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<User>(
      future: _userFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return ErrorView(message: snapshot.error.toString());
        }

        final user = snapshot.data;
        if (user == null) {
          return const EmptyView(message: 'No user found');
        }

        return UserCard(user: user);
      },
    );
  }
}
```

如果点击按钮才触发请求，也不要把请求写进 `build`，而是在事件里更新 `_userFuture`：

```dart
ElevatedButton(
  onPressed: () {
    setState(() {
      _userFuture = widget.api.fetchUser(widget.userId);
    });
  },
  child: const Text('Retry'),
)
```

## 坑

- 在 `build` 中写 `future: fetchData()`，会把普通重建变成重复请求。
- 只判断 `snapshot.hasData`，容易把错误态、空态和加载态混在一起。
- 参数变化后忘记重建 Future，会让 UI 继续展示旧参数的数据。
- 把 `FutureBuilder` 当作全局状态管理工具，会让刷新、缓存、分页和取消请求越来越难控制。

## 检查

- 搜索 `FutureBuilder` 附近是否存在 `future: someFunction()` 这种直接调用。
- 父组件 `setState` 或切换主题时，网络请求不应重复发起。
- 改变 `userId` 这类输入参数时，页面应重新请求并展示新数据。
- loading、error、empty、data 四种状态都有明确 UI，而不是只写一个 `hasData` 分支。
