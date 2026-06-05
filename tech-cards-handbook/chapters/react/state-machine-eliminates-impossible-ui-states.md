# 状态机消除步骤流里的不可能状态

## 问题

多步骤流程常被拆成多个布尔值或互相独立的字段：`isEditing`、`isSaving`、`isSuccess`、`error` 同时存在。字段一多，就容易出现“既保存中又成功”“有错误但仍显示成功页”这类 UI 不可能状态。

```tsx
function ProfileWizard() {
  const [isEditing, setIsEditing] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');

  async function submit() {
    setIsSaving(true);
    setError('');
    try {
      await saveDraft();
      setIsSuccess(true);
      // 忘记 setIsEditing(false) 或 setIsSaving(false)，UI 就会进入矛盾组合
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Save failed');
    }
  }

  return <button onClick={() => void submit()}>Save</button>;
}
```

## 解决

把“页面当前处于哪一种状态”建模成 discriminated union。每个状态只携带自己需要的数据，组件根据 `state.status` 渲染；状态转移集中在 reducer 中表达。

```tsx
type Profile = { name: string; email: string };

type WizardState =
  | { status: 'editing'; draft: Profile }
  | { status: 'saving'; draft: Profile }
  | { status: 'success'; profile: Profile }
  | { status: 'failure'; draft: Profile; message: string };

type WizardAction =
  | { type: 'CHANGE_FIELD'; field: keyof Profile; value: string }
  | { type: 'SUBMIT' }
  | { type: 'RESOLVE'; profile: Profile }
  | { type: 'REJECT'; message: string }
  | { type: 'EDIT_AGAIN' };

function wizardReducer(state: WizardState, action: WizardAction): WizardState {
  switch (action.type) {
    case 'CHANGE_FIELD':
      if (state.status !== 'editing' && state.status !== 'failure') {
        return state;
      }
      return {
        status: 'editing',
        draft: { ...state.draft, [action.field]: action.value },
      };
    case 'SUBMIT':
      if (state.status !== 'editing' && state.status !== 'failure') {
        return state;
      }
      return { status: 'saving', draft: state.draft };
    case 'RESOLVE':
      return { status: 'success', profile: action.profile };
    case 'REJECT':
      if (state.status !== 'saving') {
        return state;
      }
      return { status: 'failure', draft: state.draft, message: action.message };
    case 'EDIT_AGAIN':
      if (state.status === 'success') {
        return { status: 'editing', draft: state.profile };
      }
      return state;
    default:
      return state;
  }
}

const initialWizardState: WizardState = {
  status: 'editing',
  draft: { name: '', email: '' },
};

function ProfileWizard() {
  const [state, dispatch] = useReducer(wizardReducer, initialWizardState);

  if (state.status === 'success') {
    return <button onClick={() => dispatch({ type: 'EDIT_AGAIN' })}>Edit again</button>;
  }

  const draft = state.draft;
  return (
    <form onSubmit={(event: { preventDefault(): void }) => { event.preventDefault(); dispatch({ type: 'SUBMIT' }); }}>
      <input
        value={draft.name}
        disabled={state.status === 'saving'}
        onChange={(event: { target: { value: string } }) => dispatch({ type: 'CHANGE_FIELD', field: 'name', value: event.target.value })}
      />
      {state.status === 'failure' && <p role="alert">{state.message}</p>}
      <button disabled={state.status === 'saving'} type="submit">
        {state.status === 'saving' ? 'Saving...' : 'Save'}
      </button>
    </form>
  );
}
```

## 要点

- **状态不是布尔变量集合**：当多个布尔值互斥时，优先把它们合并成一个 `status`。
- **每个状态只带合法数据**：`success` 带 `profile`，`failure` 带 `draft` 和 `message`，避免到处判断字段是否为空。
- **转移比赋值重要**：reducer 表达“哪些事件可以从当前状态走到下一状态”，无效事件直接保持原状态。
- **异步结果也要回到状态机**：请求成功/失败只分发 `RESOLVE`/`REJECT`，不要在 `then/catch` 里散落多个 setter。
- **不要过度建模**：只有两个简单状态的开关不需要状态机；步骤流、提交流、审批流更适合。

## 检查方式

- 画出当前 UI 的所有 `status`，确认每个状态都有唯一渲染分支。
- 搜索同一个组件里的多个互斥布尔值，如 `isLoading`、`isSuccess`、`isError`，优先改成联合类型。
- 给 reducer 写表格测试：当前状态 + action => 下一状态，覆盖非法转移。
