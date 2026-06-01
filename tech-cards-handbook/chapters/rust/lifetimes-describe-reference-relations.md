# 生命周期标注描述引用关系

**问题**：生命周期是不是让变量活得更久？

**要点**：

- 生命周期不改变值的存活时间；值什么时候释放仍由所有权和作用域决定。
- 生命周期标注描述“返回引用和哪些输入引用有关”，帮助编译器排除悬垂引用。
- 大多数函数可以依靠生命周期省略规则；当一个返回引用可能来自多个输入时，才常常需要显式标注。
- 结构体里保存引用时，也要把结构体实例的有效期绑定到被引用数据的有效期上。

**示例**：

```rust
#[derive(Debug, PartialEq)]
struct Highlight<'a> {
    source: &'a str,
    keyword: &'a str,
}

fn longest<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() {
        left
    } else {
        right
    }
}

fn first_sentence(text: &str) -> &str {
    text.split('.').next().unwrap_or(text)
}

fn build_highlight<'a>(source: &'a str, keyword: &'a str) -> Highlight<'a> {
    Highlight { source, keyword }
}

fn main() {
    let article = String::from("Rust lifetimes describe relationships. They do not extend values.");
    let note = String::from("borrow checker");

    let sentence = first_sentence(&article);
    assert_eq!(sentence, "Rust lifetimes describe relationships");

    let winner = longest(sentence, note.as_str());
    assert_eq!(winner, "Rust lifetimes describe relationships");

    let highlight = build_highlight(&article, "lifetimes");
    assert_eq!(
        highlight,
        Highlight {
            source: article.as_str(),
            keyword: "lifetimes",
        }
    );

    println!("winner: {winner}");
    println!("highlight keyword: {}", highlight.keyword);
}
```

**坑**：生命周期标注不是“修复悬垂引用”的魔法。如果返回引用指向函数内部新建的局部变量，标注也救不了；应该返回拥有所有权的 `String`，或让返回引用来自调用方传入的数据。

```text
这类代码无法通过编译，因为 returned 引用会指向函数结束后被释放的局部变量：

fn broken<'a>() -> &'a str {
    let temporary = String::from("gone");
    temporary.as_str()
}
```

**检查**：返回引用时，能否明确说出它来自哪个输入？结构体保存引用时，能否说清楚结构体实例不能比被引用的数据活得更久？
