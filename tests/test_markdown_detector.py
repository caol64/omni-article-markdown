from omni_article_markdown.markdown_detector import extract_markdown_title, looks_like_markdown

SAMPLE_MD = """# 墨探 (omni-article-markdown)

轻松将网页文章转换为 `Markdown` 格式。

## 安装

```sh
pipx install omni-article-markdown
```

- 支持大部分 html 元素转换
- 支持 katex 公式

|站点|链接|
--|--
|Medium|[link](https://medium.com)|
"""

HTML_PAGE = """<!DOCTYPE html>
<html><head><title>Example</title></head>
<body><article><h1>Hello</h1><p>World</p></article></body></html>
"""


def test_looks_like_markdown_positive():
    assert looks_like_markdown(SAMPLE_MD) is True


def test_looks_like_markdown_plain_text_negative():
    # 404 之类纯文本，无任何结构信号
    assert looks_like_markdown("404: Not Found") is False


def test_looks_like_markdown_html_negative():
    assert looks_like_markdown(HTML_PAGE) is False


def test_looks_like_markdown_empty_negative():
    assert looks_like_markdown("") is False
    assert looks_like_markdown("   \n\n  ") is False


def test_looks_like_markdown_prose_negative():
    # 纯散文：只有一个链接，不满足 ≥2 类结构信号
    prose = "这是一段普通文字，附带一个 [链接](https://example.com)。" * 20
    assert looks_like_markdown(prose) is False


def test_looks_like_markdown_requires_two_signals():
    assert looks_like_markdown("# 只有标题") is False
    assert looks_like_markdown("# 标题\n\n- 列表项") is True


def test_extract_markdown_title_h1():
    assert extract_markdown_title(SAMPLE_MD) == "墨探 (omni-article-markdown)"


def test_extract_markdown_title_fallback_to_first_line():
    assert extract_markdown_title("[![img](x)](y)\n\n正文") == "[![img](x)](y)"


def test_extract_markdown_title_plain_text_returns_empty():
    # 无任何标题信息时返回空串，由调用方决定回退策略（避免生成空的 "# " 一级标题）
    assert extract_markdown_title("404: Not Found") == ""


def test_extract_markdown_title_empty():
    assert extract_markdown_title("") == ""
