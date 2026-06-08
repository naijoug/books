# 请求状态和数据 schema 分层

**问题**：页面请求接口时，常把 `loading`、`error`、原始 JSON、已验证数据混在一个 `state` 里。结果是 UI 分支写不全、错误类型不清楚，甚至在数据还没过 schema 边界时就被当成领域对象使用。怎样让请求生命周期和可信数据边界都保持清晰？

**要点**：

- 请求生命周期用 discriminated union 表达：`idle`、`loading`、`success`、`failure`，不要用多个布尔值拼状态。
- `success.data` 只放已经通过 decoder/schema 验证的领域对象；原始 payload 不进入业务 state。
- schema 错误、网络错误、业务错误分开建模，UI 才能给出不同恢复路径。
- reducer 或状态转换函数只接收“已分类事件”，不要在渲染组件里散落 `as` 和 `try/catch`。
- 这张卡片和 `external-api-response-schema-boundary.md` 配合使用：先解码 payload，再进入请求状态机。

**示例**：

```typescript
type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

type ApiArticle = {
  id: string;
  title: string;
  summary: string;
};

type DecodeError = {
  kind: "decode";
  field: string;
  message: string;
};

type NetworkError = {
  kind: "network";
  message: string;
};

type RequestError = DecodeError | NetworkError;

type ArticleState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: ApiArticle }
  | { status: "failure"; error: RequestError };

type ArticleEvent =
  | { type: "request_started" }
  | { type: "request_succeeded"; data: ApiArticle }
  | { type: "request_failed"; error: RequestError };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function decodeArticle(payload: unknown): Result<ApiArticle, DecodeError> {
  if (!isRecord(payload)) {
    return { ok: false, error: { kind: "decode", field: "root", message: "expected object" } };
  }

  if (typeof payload.id !== "string" || payload.id.length === 0) {
    return { ok: false, error: { kind: "decode", field: "id", message: "expected non-empty string" } };
  }

  if (typeof payload.title !== "string" || payload.title.length === 0) {
    return { ok: false, error: { kind: "decode", field: "title", message: "expected non-empty string" } };
  }

  if (typeof payload.summary !== "string") {
    return { ok: false, error: { kind: "decode", field: "summary", message: "expected string" } };
  }

  return {
    ok: true,
    value: {
      id: payload.id,
      title: payload.title,
      summary: payload.summary,
    },
  };
}

function reduceArticleState(state: ArticleState, event: ArticleEvent): ArticleState {
  switch (event.type) {
    case "request_started":
      return { status: "loading" };
    case "request_succeeded":
      return { status: "success", data: event.data };
    case "request_failed":
      return { status: "failure", error: event.error };
    default: {
      const exhaustive: never = event;
      return exhaustive;
    }
  }
}

async function loadArticle(response: Response): Promise<ArticleEvent> {
  if (!response.ok) {
    return {
      type: "request_failed",
      error: { kind: "network", message: `HTTP ${response.status}` },
    };
  }

  const payload: unknown = await response.json();
  const decoded = decodeArticle(payload);

  if (!decoded.ok) {
    return { type: "request_failed", error: decoded.error };
  }

  return { type: "request_succeeded", data: decoded.value };
}

function renderArticleState(state: ArticleState): string {
  switch (state.status) {
    case "idle":
      return "等待加载文章";
    case "loading":
      return "正在加载文章";
    case "success":
      return `${state.data.title}: ${state.data.summary}`;
    case "failure":
      return state.error.kind === "decode"
        ? `接口格式错误：${state.error.field} ${state.error.message}`
        : `网络错误：${state.error.message}`;
    default: {
      const exhaustive: never = state;
      return exhaustive;
    }
  }
}

async function refreshArticle(current: ArticleState, response: Response): Promise<ArticleState> {
  const loading = reduceArticleState(current, { type: "request_started" });
  const event = await loadArticle(response);
  return reduceArticleState(loading, event);
}
```

最小验证：把上面的代码保存为 `request-state-keeps-schema-data-separate.ts`，执行 `npx -y -p typescript@5.9.3 tsc --noEmit --strict --lib es2020,dom request-state-keeps-schema-data-separate.ts`；如果没有类型错误，说明请求生命周期、schema 解码和 UI 渲染分支已经被类型系统串起来。

**坑**：不要在 `success` 里同时放 `raw` 和 `data`，也不要把 `error: string` 当成所有失败原因。原始 payload 留在 decoder 内部；UI state 只保留已分类、可展示、可恢复的信息。

**检查**：检查请求代码时，看 `success.data` 是否一定来自 decoder/schema，失败分支是否能区分网络和格式错误，状态 union 是否覆盖了加载、成功、失败和空闲四类生命周期，以及渲染函数是否有 `never` 穷尽检查。
