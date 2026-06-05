# 请求重试要有边界和退避

## 问题

网络请求失败后直接“立刻再试一次”很容易把临时抖动放大成雪崩：用户端连续发请求，服务端刚恢复又被重试流量打满。相反，如果完全不重试，用户会因为一次短暂断网或 502 直接看到失败页。React 组件里的读取请求需要把重试设计成有边界、可取消、可解释的状态机。

## 要点

- 只重试适合重试的失败：网络错误、超时、`429`、`5xx`；不要自动重试 `400`、`401`、`403`、`404` 这类语义失败。
- 重试次数必须有上限，并使用指数退避；生产环境最好再加 jitter，避免所有客户端同一时间重试。
- 组件卸载或查询条件变化时要取消等待中的退避计时和请求，不能让旧重试链继续写状态。
- UI 要暴露“第几次重试 / 是否最终失败”，不要让用户只看到无限加载。
- 写操作的自动重试要更谨慎：除非接口具备幂等键，否则可能重复创建订单、重复扣费或重复提交表单。

## 示例

```tsx
import { useEffect, useState } from 'react';

type Product = { id: string; name: string; price: number };
type ProductState =
  | { status: 'loading'; attempt: number }
  | { status: 'success'; product: Product }
  | { status: 'error'; message: string; attempts: number };

function delay(ms: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(resolve, ms);
    signal.addEventListener(
      'abort',
      () => {
        window.clearTimeout(timer);
        reject(new DOMException('aborted', 'AbortError'));
      },
      { once: true },
    );
  });
}

function shouldRetry(error: unknown): boolean {
  return error instanceof TypeError;
}

async function fetchProduct(productId: string, signal: AbortSignal): Promise<Product> {
  const response = await fetch(`/api/products/${productId}`, { signal });
  if (response.status === 429 || response.status >= 500) {
    throw new TypeError(`temporary failure: ${response.status}`);
  }
  if (!response.ok) {
    throw new Error(`cannot load product: ${response.status}`);
  }
  return response.json() as Promise<Product>;
}

async function fetchWithBackoff(
  productId: string,
  signal: AbortSignal,
  onAttempt: (attempt: number) => void,
): Promise<Product> {
  const maxAttempts = 3;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    onAttempt(attempt);
    try {
      return await fetchProduct(productId, signal);
    } catch (error: unknown) {
      if (attempt === maxAttempts || !shouldRetry(error)) {
        throw error;
      }
      await delay(300 * 2 ** (attempt - 1), signal);
    }
  }
  throw new Error('unreachable retry state');
}

export function ProductCard({ productId }: { productId: string }) {
  const [state, setState] = useState<ProductState>({ status: 'loading', attempt: 1 });

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: 'loading', attempt: 1 });

    fetchWithBackoff(productId, controller.signal, (attempt) => {
      setState({ status: 'loading', attempt });
    })
      .then((product) => {
        setState({ status: 'success', product });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return;
        }
        const message = error instanceof Error ? error.message : 'unknown error';
        setState({ status: 'error', message, attempts: 3 });
      });

    return () => {
      controller.abort();
    };
  }, [productId]);

  if (state.status === 'loading') {
    return <p>Loading product... attempt {state.attempt}</p>;
  }
  if (state.status === 'error') {
    return <p role="alert">Retried {state.attempts} times: {state.message}</p>;
  }
  return <p>{state.product.name} · {state.product.price}</p>;
}
```

## 坑

- 把所有错误都当成临时错误，会让权限失败、参数错误和不存在的资源被重复请求。
- 没有最大次数的重试，本质上是一个隐藏的轮询器。
- 在 `useEffect` cleanup 里只 abort 请求、不取消退避 timer，旧链路仍可能在等待结束后继续下一次请求。
- 多个组件各自实现重试策略时容易叠加放大；共享数据层最好统一 retry policy。

## 检查

- 断网或模拟 `500` 时，Network 面板最多出现 3 次请求，间隔逐步拉长。
- 模拟 `404` 时不自动重试，直接进入可解释的失败状态。
- 快速切换 `productId` 或卸载组件后，旧请求链不会继续发下一次重试，也不会写入旧状态。
- 对创建、支付、提交等写操作，只有在接口具备幂等键时才启用自动重试。
