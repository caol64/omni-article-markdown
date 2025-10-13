import pytest
from bs4.element import NavigableString, AttributeValueList
from omni_article_markdown.utils import (
    is_sequentially_increasing,
    move_spaces,
    to_snake_case,
    collapse_spaces,
    extract_domain,
    detect_language,
    filter_tag,
    get_attr_text,
    get_og_url,
    get_og_site_name,
    get_og_description,
    get_canonical_url,
    is_matched_canonical,
    get_og_title,
    get_tag_text,
    get_title,
)


# --------------------------
# 测试 is_sequentially_increasing
# --------------------------
def test_is_sequentially_increasing_true():
    code = "1\n2\n3\n4"
    assert is_sequentially_increasing(code) is True


def test_is_sequentially_increasing_false():
    code = "1\n3\n5"
    assert is_sequentially_increasing(code) is False


def test_is_sequentially_increasing_non_numeric():
    code = "a\nb\nc"
    assert is_sequentially_increasing(code) is False


# --------------------------
# move_spaces
# --------------------------
def test_move_spaces():
    assert move_spaces("**hello  **", "**") == "**hello**  "
    assert move_spaces("**hello **", "**") == "**hello** "
    assert move_spaces("**hello world**", "**") == "**hello world**"


# --------------------------
# to_snake_case
# --------------------------
def test_to_snake_case():
    assert to_snake_case("HelloWorld") == "helloworld"
    assert to_snake_case("Hello World!") == "hello_world"
    assert to_snake_case("Already_snake_case") == "already_snake_case"


# --------------------------
# collapse_spaces
# --------------------------
def test_collapse_spaces():
    assert collapse_spaces("a   b\tc\nd") == "a b c d"


# --------------------------
# extract_domain
# --------------------------
def test_extract_domain():
    assert extract_domain("https://example.com/path?q=1") == "https://example.com"
    assert extract_domain("http://abc.xyz") == "http://abc.xyz"
    assert extract_domain("ftp://example.com") is None
    assert extract_domain("not_a_url") is None


# --------------------------
# detect_language
# --------------------------
def test_detect_language_placeholder():
    assert detect_language("file.py", "print('hi')") == ""


# --------------------------
# filter_tag
# --------------------------
def test_filter_tag_with_tag(make_soup):
    soup = make_soup("<div></div>")
    el = soup.div
    assert filter_tag(el) == el


def test_filter_tag_with_none_or_text():
    text_node = NavigableString("text")
    assert filter_tag(None) is None
    assert filter_tag(text_node) is None


# --------------------------
# get_attr_text
# --------------------------
def test_get_attr_text():
    assert get_attr_text(" hello ") == "hello"
    assert get_attr_text(AttributeValueList(["a", "b", "c"])) == "a b c"
    assert get_attr_text(None) == ""


# --------------------------
# meta/og tag 相关
# --------------------------
HTML_DOC = """
<html>
<head>
    <title>Example Title</title>
    <meta property="og:url" content="https://example.com/page" />
    <meta property="og:site_name" content="Example Site" />
    <meta property="og:description" content="This is a description." />
    <meta property="og:title" content="OG Title" />
    <link rel="canonical" href="https://example.com/page" />
</head>
<body><h1>Hello</h1></body>
</html>
"""


@pytest.fixture
def soup(make_soup):
    return make_soup(HTML_DOC)


def test_get_og_url(soup):
    assert get_og_url(soup) == "https://example.com/page"


def test_get_og_site_name(soup):
    assert get_og_site_name(soup) == "Example Site"


def test_get_og_description(soup):
    assert get_og_description(soup) == "This is a description."


def test_get_og_title(soup):
    assert get_og_title(soup) == "OG Title"


def test_get_canonical_url(soup):
    assert get_canonical_url(soup) == "https://example.com/page"


def test_is_matched_canonical_true(soup):
    assert is_matched_canonical("https://example.com", soup) is True


def test_is_matched_canonical_false(soup):
    assert is_matched_canonical("https://other.com", soup) is False


# --------------------------
# get_tag_text
# --------------------------
def test_get_tag_text(make_soup):
    soup = make_soup('<meta name="description" content="abc" />')
    tag = filter_tag(soup.find("meta"))
    assert get_tag_text(tag, "content") == "abc"
    assert get_tag_text(tag, "missing") == ""
    assert get_tag_text(None, "content") == ""


# --------------------------
# get_title
# --------------------------
def test_get_title(soup):
    assert get_title(soup) == "Example Title"


def test_get_title_no_title(make_soup):
    soup = make_soup("<html><head></head></html>")
    assert get_title(soup) == ""
