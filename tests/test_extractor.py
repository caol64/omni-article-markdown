from bs4.element import Tag

from omni_article_markdown.extractor import (
    Article,
    DefaultExtractor,
    extract_article_from_soup,
    remove_duplicate_titles,
)

# ---- mock utils ----

def make_html(content: str, title="Page Title", description="Desc", url="https://example.com") -> str:
    return f"""
    <html>
        <head>
            <title>{title}</title>
            <meta property="og:description" content="{description}">
            <meta property="og:url" content="{url}">
        </head>
        <body>
            {content}
        </body>
    </html>
    """


def test_extract_article_from_soup_basic(make_soup):
    html = "<html><body><article><p>Hello</p></article></body></html>"
    soup = make_soup(html)
    tag = extract_article_from_soup(soup, ("article", None))
    assert tag is not None
    assert tag.name == "article"
    assert "Hello" in tag.text


def test_default_extractor_basic_behavior(make_soup):
    extractor = DefaultExtractor()
    html = make_html("<article><p>Hello World</p></article>")
    soup = make_soup(html)

    assert extractor.can_handle(soup) is True
    assert isinstance(extractor.article_container(), list | tuple)


def test_cleaning_tags_and_attrs(make_soup):
    html = make_html("""
        <article>
            <p>Visible</p>
            <style>p{color:red}</style>
            <p style="display:none">Hidden</p>
            <div hidden>Invisible</div>
            <!-- comment -->
        </article>
    """)
    extractor = DefaultExtractor()
    article = extractor.extract(make_soup(html))
    assert article is not None
    assert isinstance(article.body, Tag)
    text = article.body.get_text()
    # 不应包含隐藏元素、style、注释内容
    assert "Visible" in text
    assert "Hidden" not in text
    assert "Invisible" not in text
    assert "color:red" not in text


def test_extract_metadata(make_soup):
    html = make_html("<article><p>Body</p></article>", title="Hello", description="A test desc", url="https://abc.com")
    soup = make_soup(html)
    extractor = DefaultExtractor()

    assert extractor.extract_title(soup) == "Hello"
    assert extractor.extract_description(soup) == "A test desc"
    assert extractor.extract_url(soup) == "https://abc.com"


def test_remove_duplicate_titles(make_soup):
    html = "<article><h1>Same Title</h1><p>Body text</p></article>"
    soup = make_soup(html)
    article = Article(title="Same Title", url=None, description=None, body=soup.article)
    remove_duplicate_titles(article)

    # 标题应保持一致
    assert article.title == "Same Title"
    # H1 应被删除
    assert article.body.find("h1") is None


def test_remove_duplicate_titles_different(make_soup):
    html = "<article><h1>Other Title</h1><p>Body text</p></article>"
    soup = make_soup(html)
    article = Article(title="Main Page", url=None, description=None, body=soup.article)
    remove_duplicate_titles(article)

    # 原标题不变，H1 保留
    assert article.title == "Main Page"
    assert article.body.find("h1") is not None


class CustomExtractor(DefaultExtractor):
    def can_handle(self, soup):
        title = soup.title.text.strip() if soup.title else ""
        return "Special" in title

    def article_container(self):
        return ("body", None)


def test_custom_extractor_can_handle(make_soup):
    html = make_html("<p>Hello</p>", title="Special Page")
    extractor = CustomExtractor()
    soup = make_soup(html)
    assert extractor.can_handle(soup) is True

    article = extractor.extract(soup)
    assert article is not None
    assert isinstance(article.body, Tag)
    assert "Hello" in article.body.text
