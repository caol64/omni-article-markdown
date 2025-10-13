from omni_article_markdown.extractor import Article
from omni_article_markdown.parser import HtmlMarkdownParser


def test_basic_paragraph(make_soup):
    html = "<p>Hello world</p>"
    article = Article("Test", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    title, md = parser.parse()
    assert "# Test" in md
    assert "Hello world" in md


def test_heading_and_strong(make_soup):
    html = "<h2>Subtitle</h2><p><strong>bold</strong> and <em>italic</em></p>"
    article = Article("Title", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "## Subtitle" in md
    assert "**bold**" in md
    assert "*italic*" in md


def test_link_parsing(make_soup):
    html = '<p><a href="https://example.com">Example</a></p>'
    article = Article("Title", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "[Example](https://example.com)" in md


def test_unordered_list(make_soup):
    html = "<ul><li>Apple</li><li>Banana</li></ul>"
    article = Article("Fruits", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "- Apple" in md
    assert "- Banana" in md


def test_ordered_list(make_soup):
    html = "<ol><li>One</li><li>Two</li></ol>"
    article = Article("Numbers", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "1. One" in md
    assert "2. Two" in md


def test_blockquote(make_soup):
    html = "<blockquote><p>Quote me</p></blockquote>"
    article = Article("Quote", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "> Quote me" in md


def test_codeblock(make_soup):
    html = "<pre><code>print('Hello')</code></pre>"
    article = Article("Code", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "```" in md
    assert "print('Hello')" in md


def test_inline_code(make_soup):
    html = "<p>Run <code>ls -al</code> command.</p>"
    article = Article("Cmd", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "`ls -al`" in md


def test_image_absolute_url(make_soup):
    html = '<img src="https://example.com/image.png" alt="demo">'
    article = Article("Img", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "![demo](https://example.com/image.png)" in md


def test_image_relative_url(make_soup):
    html = '<img src="../images/demo.png" alt="demo">'
    article = Article("Img", "https://site.com/docs/page.html", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "![demo](https://site.com/images/demo.png)" in md


def test_table_parsing(make_soup):
    html = """
    <table>
        <tr><th>Name</th><th>Age</th></tr>
        <tr><td>Alice</td><td>18</td></tr>
        <tr><td>Bob</td><td>20</td></tr>
    </table>
    """
    article = Article("Table", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "| Name | Age |" in md
    assert "| Alice | 18 |" in md


def test_mathjax_equations(make_soup):
    html = "<math><semantics><annotation encoding='application/x-tex'>E=mc^2</annotation></semantics></math>"
    article = Article("Math", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "$$ E=mc^2 $$" in md


def test_post_handler_math(make_soup):
    html = "<p>\\(x+y\\) and \\[E=mc^2\\]</p>"
    article = Article("Math", "", "", make_soup(html))
    parser = HtmlMarkdownParser(article)
    _, md = parser.parse()
    assert "$x+y$" in md
    assert "$$E=mc^2$$" in md
