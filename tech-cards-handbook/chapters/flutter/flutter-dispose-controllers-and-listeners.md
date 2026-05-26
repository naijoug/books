# Flutter controller 和 listener 要成对释放

**问题**：

`TextEditingController`、`ScrollController`、`AnimationController` 这类对象通常会持有原生资源、Ticker、滚动位置或监听回调。如果只在 `initState` 里创建，却忘了在 `dispose` 中解绑和释放，页面离开后仍可能继续触发回调，带来内存泄漏、重复事件或异常日志。

这类问题在“页面反复进入退出”“列表滚动监听”“动画循环”和“输入框监听搜索”场景里最常见。

**要点**：

- 在 `State` 中创建的 controller，默认由这个 `State` 负责在 `dispose` 中释放。
- `addListener` 和 `removeListener` 要成对出现；先移除监听，再 `dispose` controller。
- `AnimationController` 需要 `vsync`，也必须在 `dispose` 中释放，否则容易留下 active ticker。
- 如果 controller 从父组件传入，通常不在子组件里释放；只释放自己创建的对象。
- 异步回调或 listener 中更新 UI 时，仍要配合 `mounted` 检查，避免页面销毁后写回状态。

**示例**：

输入监听和滚动监听都由当前页面持有时：

```dart
class SearchPage extends StatefulWidget {
  const SearchPage({super.key});

  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage>
    with SingleTickerProviderStateMixin {
  late final TextEditingController _queryController;
  late final ScrollController _scrollController;
  late final AnimationController _loadingController;

  bool _showBackToTop = false;

  @override
  void initState() {
    super.initState();

    _queryController = TextEditingController();
    _queryController.addListener(_onQueryChanged);

    _scrollController = ScrollController();
    _scrollController.addListener(_onScroll);

    _loadingController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
  }

  void _onQueryChanged() {
    final keyword = _queryController.text.trim();
    // debounce 或搜索请求可以放在这里触发；真正异步返回时仍要检查 mounted。
    debugPrint('search: $keyword');
  }

  void _onScroll() {
    final shouldShow = _scrollController.offset > 240;
    if (shouldShow == _showBackToTop) return;

    setState(() {
      _showBackToTop = shouldShow;
    });
  }

  @override
  void dispose() {
    _queryController.removeListener(_onQueryChanged);
    _queryController.dispose();

    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();

    _loadingController.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      controller: _scrollController,
      children: [
        TextField(controller: _queryController),
        if (_showBackToTop) const Text('Back to top'),
      ],
    );
  }
}
```

如果 controller 是父组件传入的，子组件只使用，不释放：

```dart
class SearchBox extends StatelessWidget {
  const SearchBox({super.key, required this.controller});

  final TextEditingController controller;

  @override
  Widget build(BuildContext context) {
    return TextField(controller: controller);
  }
}
```

**坑**：

- 在 `build` 方法里创建 controller：每次重建都会丢输入、重复监听，也很难正确释放。
- 只 `dispose` controller，忘记 `removeListener`；多数情况下 dispose 会清理内部监听，但显式成对解绑更利于审查和避免回调引用长期悬挂。
- 子组件释放了父组件传入的 controller，导致父组件后续使用时出现异常。
- listener 里直接发起异步请求并在返回后 `setState`，但没有检查 `mounted` 或取消旧请求。
- `AnimationController` 创建后忘记释放，调试台可能出现 ticker 仍然 active 的警告。

**检查**：

- 搜索 `Controller(`、`addListener`、`AnimationController`，确认同一个 `State` 的 `dispose` 中有对应释放逻辑。
- 确认 controller 不在 `build` 中创建，除非它是短生命周期且不会跨帧保留的临时对象。
- 快速反复进入退出页面，观察是否有 ticker、`setState() called after dispose()`、重复监听或内存持续增长。
- 分清 controller 的 owner：谁创建，谁释放；父传子的 controller 不由子释放。
