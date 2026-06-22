# Flutter 降级策略要放在调用方而不是 repository

## 问题

Flutter 应用经常需要在网络、缓存、登录态和表单提交之间做取舍：资料页可以先显示本地缓存，支付页不能用默认金额继续，搜索页可以展示空结果但要标记离线。如果 repository 在内部吞掉失败并返回假数据，widget / ViewModel 就无法知道当前状态是新鲜数据、缓存降级还是不可恢复错误，后续埋点、重试按钮和用户提示都会失真。

## 要点

- repository 只报告事实：返回最新数据，或抛出/返回领域错误；不要在被调方静默选择缓存、默认值或空列表。
- 调用方根据业务场景决定是否降级：资料卡片可用缓存，交易提交必须失败，搜索页可展示离线结果。
- 降级结果必须显式携带 `degraded`、`source`、`message` 或可观测事件，避免 UI 把缓存当成真实结果。
- 降级动作应和重试策略、领域错误码、恢复决策表共享同一套错误分类，不要在 widget 的 `catch` 里重新解析底层异常文案。

| 场景 | 被调方隐藏降级 | 调用方决定降级 |
|---|---|---|
| 资料页 | repository 返回缓存但不标记来源 | ViewModel 捕获 `ProfileUnavailable` 后选择缓存并设置 `degraded` |
| 支付页 | repository 返回默认限额或默认金额 | 调用方直接阻断提交并展示安全错误 |
| 搜索页 | repository 把网络错误变成空列表 | 调用方展示缓存结果、离线提示和重试入口 |
| 观测 | 日志只看到成功返回 | 埋点能区分 fresh / cache / blocked |

## 示例

```dart
// flutter-degradation-strategy-at-caller-not-callee.dart
enum ProfileSource {
  network,
  cache,
}

class Profile {
  const Profile({required this.id, required this.name});

  final String id;
  final String name;
}

class ProfileSnapshot {
  const ProfileSnapshot({
    required this.profile,
    required this.source,
    required this.degraded,
    required this.message,
  });

  final Profile profile;
  final ProfileSource source;
  final bool degraded;
  final String message;
}

sealed class ProfileError implements Exception {
  const ProfileError(this.message);

  final String message;
}

final class ProfileUnavailable extends ProfileError {
  const ProfileUnavailable(super.message);
}

class ProfileRepository {
  ProfileRepository({required this.remoteProfile, required this.cachedProfile});

  final Profile? remoteProfile;
  final Profile? cachedProfile;

  Future<Profile> fetchFreshProfile(String userId) async {
    final fresh = remoteProfile;
    if (fresh == null) {
      throw const ProfileUnavailable('profile service unavailable');
    }
    return fresh;
  }

  Future<Profile?> readCachedProfile(String userId) async {
    return cachedProfile;
  }
}

class ProfileViewModel {
  ProfileViewModel(this.repository);

  final ProfileRepository repository;

  Future<ProfileSnapshot> loadProfileCard(String userId) async {
    try {
      final fresh = await repository.fetchFreshProfile(userId);
      return ProfileSnapshot(
        profile: fresh,
        source: ProfileSource.network,
        degraded: false,
        message: '资料已更新',
      );
    } on ProfileUnavailable {
      final cached = await repository.readCachedProfile(userId);
      if (cached == null) {
        rethrow;
      }

      return ProfileSnapshot(
        profile: cached,
        source: ProfileSource.cache,
        degraded: true,
        message: '暂时显示离线资料',
      );
    }
  }

  Future<void> submitPayment(String userId) async {
    try {
      await repository.fetchFreshProfile(userId);
    } on ProfileUnavailable {
      throw const ProfileUnavailable('支付前必须确认最新资料');
    }
  }
}

Future<void> main() async {
  final repository = ProfileRepository(
    remoteProfile: null,
    cachedProfile: const Profile(id: 'u_1', name: 'cached user'),
  );
  final viewModel = ProfileViewModel(repository);

  final card = await viewModel.loadProfileCard('u_1');
  assert(card.degraded);
  assert(card.source == ProfileSource.cache);
  assert(card.message == '暂时显示离线资料');

  var paymentBlocked = false;
  try {
    await viewModel.submitPayment('u_1');
  } on ProfileUnavailable catch (error) {
    paymentBlocked = error.message == '支付前必须确认最新资料';
  }
  assert(paymentBlocked);
}
```

同一个 repository 只暴露“新鲜资料是否可用”和“是否有缓存”两个事实；资料卡片调用方允许缓存降级，支付调用方则禁止降级并传播错误。这样 review 时可以直接在调用方看到业务容忍度，而不是猜 repository 是否偷偷返回了假成功。

## 坑

- **repository 返回缓存但不标记**：UI 继续展示“已同步”状态，用户误以为看到的是最新数据。
- **所有调用方共用一个降级默认值**：资料页、支付页、后台同步的风险级别不同，不能由被调方统一决定。
- **把空列表当作失败兜底**：搜索失败时返回 `[]` 会让用户以为没有结果，也会污染推荐和埋点。
- **降级态没有重试入口**：如果 `degraded` 只是一段文案，后续无法判断是否应该显示刷新按钮、离线徽标或告警。
- **异步写状态越过生命周期**：调用方决定降级后，写入 widget / ViewModel state 前仍要检查 `mounted`、请求 token 或 dispose 状态。

## 检查

- repository / adapter 是否只返回事实或领域错误，而不是静默返回缓存、默认值或空集合？
- 每个调用方是否显式说明自己是否允许降级，以及允许降级时使用哪个数据源？
- 降级结果是否携带 `degraded`、`source`、安全文案和可观测事件，避免被当成普通成功？
- 支付、权限、写操作等高风险路径是否明确禁止降级，并把错误交给恢复决策表处理？
- 与 [`flutter-external-error-codes-domain-defined-not-leaked.md`](flutter-external-error-codes-domain-defined-not-leaked.md)、[`flutter-retry-policy-explicit-not-hidden-loop.md`](flutter-retry-policy-explicit-not-hidden-loop.md) 和 [`flutter-error-recovery-decision-table.md`](flutter-error-recovery-decision-table.md) 一起检查：错误码、重试、降级和 UI 恢复动作是否由同一套调用方决策驱动。
- 对照 Swift 的 [`../swift/swift-degradation-strategy-at-caller-not-callee.md`](../swift/swift-degradation-strategy-at-caller-not-callee.md)、TypeScript 的 [`../typescript/degradation-strategy-at-caller-not-callee.md`](../typescript/degradation-strategy-at-caller-not-callee.md) 和 Python 的 [`../python/degradation-strategy-at-caller-not-callee.md`](../python/degradation-strategy-at-caller-not-callee.md)，确认移动端和后端都没有在被调方隐藏假成功。
