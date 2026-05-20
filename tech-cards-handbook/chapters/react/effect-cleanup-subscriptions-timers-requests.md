# Effect 必须清理订阅、定时器和请求

**问题**：组件卸载后，为什么定时器还在跑或请求还在 setState？

**要点**：

- effect 可以返回清理函数。
- 定时器、订阅、事件监听、请求取消都应清理。
- `useEffect` 回调本身不要写成 `async`，因为它需要返回清理函数或 `undefined`。

**示例**：

```tsx
useEffect(() => {
  const timer = window.setInterval(() => {
    console.log("tick");
  }, 1000);

  return () => window.clearInterval(timer);
}, []);

useEffect(() => {
  async function load() {
    const data = await fetchData();
    setData(data);
  }

  load();
}, []);
```

**坑**：没有依赖数组的 effect 每次 render 都执行；依赖里放每次新建的对象或函数，也会导致重复执行。

**检查**：每个 effect 是否只做一件外部同步？是否有必要的清理？
