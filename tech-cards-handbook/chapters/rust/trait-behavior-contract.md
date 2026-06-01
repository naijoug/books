# trait 表达行为契约

**问题**：如何让不同类型共享一组能力，同时不把调用方绑死在某个具体类型上？

**要点**：

- trait 定义“调用方可以依赖的行为集合”，不是定义“这个对象内部长什么样”。
- 泛型参数加 trait bound 会在编译期做静态分发，适合性能敏感和类型已知的场景。
- `dyn Trait` 会通过 trait object 做运行时分发，适合把多种实现放进同一个集合或在运行时组合。
- 小而稳定的 trait 更容易测试、组合和替换；过大的 trait 会把实现方和调用方一起锁死。

**示例**：

```rust
trait Render {
    fn render(&self) -> String;
}

trait Clickable {
    fn click(&mut self);
}

struct Button {
    label: String,
    clicks: u32,
}

impl Button {
    fn new(label: &str) -> Self {
        Self {
            label: label.to_string(),
            clicks: 0,
        }
    }
}

impl Render for Button {
    fn render(&self) -> String {
        format!("<button>{} ({})</button>", self.label, self.clicks)
    }
}

impl Clickable for Button {
    fn click(&mut self) {
        self.clicks += 1;
    }
}

struct Text {
    value: String,
}

impl Text {
    fn new(value: &str) -> Self {
        Self {
            value: value.to_string(),
        }
    }
}

impl Render for Text {
    fn render(&self) -> String {
        format!("<span>{}</span>", self.value)
    }
}

// 静态分发：编译器知道具体类型，调用处可以被内联优化。
fn render_static<T: Render>(component: &T) -> String {
    component.render()
}

// 运行时分发：调用方只知道“它能 Render”，不知道具体是哪种组件。
fn render_page(components: &[Box<dyn Render>]) -> String {
    components
        .iter()
        .map(|component| component.render())
        .collect::<Vec<_>>()
        .join("\n")
}

fn press_twice<T: Clickable + Render>(component: &mut T) -> String {
    component.click();
    component.click();
    component.render()
}

fn main() {
    let title = Text::new("Settings");
    let mut save = Button::new("Save");

    assert_eq!(render_static(&title), "<span>Settings</span>");
    assert_eq!(press_twice(&mut save), "<button>Save (2)</button>");

    let page: Vec<Box<dyn Render>> = vec![
        Box::new(title),
        Box::new(save),
        Box::new(Text::new("Done")),
    ];

    let html = render_page(&page);
    assert!(html.contains("<button>Save (2)</button>"));
    assert!(html.contains("<span>Done</span>"));

    println!("{html}");
}
```

**坑**：不要把 trait 设计成“万能服务接口”。例如把 `render`、`click`、`save_to_db`、`send_metric` 都塞进一个 trait，会让只需要渲染的调用方也被迫依赖无关能力。优先从调用方真正需要的稳定行为切出小 trait，再用 `T: TraitA + TraitB` 组合。

**检查**：这个 trait 是否表达了稳定行为，而不是临时为了 mock 抽出来的对象？调用方是否只看见它真正需要的方法？
