import re
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList, NavigableString, PageElement, Tag


def is_sequentially_increasing(code: str) -> bool:
    try:
        # 解码并按换行符拆分
        numbers = [int(line.strip()) for line in code.split("\n") if line.strip()]
        # 单个数字无法构成递增序列,只有两个及以上数字才能判定为行号列
        if len(numbers) < 2:
            return False
        # 检查是否递增
        return all(numbers[i] + 1 == numbers[i + 1] for i in range(len(numbers) - 1))
    except ValueError:
        return False  # 处理非数字情况


def move_spaces(input_string: str, suffix: str) -> str:
    # 使用正则表达式匹配以指定的suffix结尾，且suffix之前有空格的情况
    escaped_suffix = re.escape(suffix)  # 处理正则中的特殊字符
    pattern = rf"(.*?)\s+({escaped_suffix})$"
    match = re.search(pattern, input_string)
    if match:
        # 获取字符串的主体部分（不含空格）和尾部的 '**'
        main_part = match.group(1)
        stars = match.group(2)
        # 计算空格的数量并将空格移动到 '**' 后
        space_count = len(input_string) - len(main_part) - len(stars)
        return f"{main_part}{stars}{' ' * space_count}"
    return input_string


def to_snake_case(input_string: str) -> str:
    input_string = "".join(char if char.isalnum() else " " for char in input_string)
    snake_case_string = "_".join(word.lower() for word in input_string.split())
    return snake_case_string


def collapse_spaces(text: str) -> str:
    """
    将多个连续空格（包括换行和 Tab）折叠成一个空格。
    """
    return re.sub(r"\s+", " ", text)


def utf8_size(text: str) -> int:
    return len(text.encode("utf-8"))


# CJK 统一区间：日文假名、CJK 基本/扩展 A、兼容表意文字、全角标点与空格
_CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff01-\uff5e\u3000-\u303f]")

# cl100k 类 BPE 的经验系数：拉丁文本约 3.5 字节/token（含空格与标点摊薄），CJK 约 2.2 字节/token
_LATIN_BYTES_PER_TOKEN = 3.5
_CJK_BYTES_PER_TOKEN = 2.2


def count_tokens(text: str | list[str]) -> int:
    """
    按内容类型分段的近似 token 计数：
    CJK 字符与其余文本分别折算，避免纯英文被整体 ÷2.5 高估约 30%。
    """
    if isinstance(text, list):
        text = "\n".join(text)
    if not text:
        return 0
    cjk_bytes = sum(len(ch.encode("utf-8")) for ch in text if _CJK_RE.match(ch))
    latin_bytes = utf8_size(text) - cjk_bytes
    # 非空文本至少计 1 token，避免短片段被 int() 抹零导致调用方死循环
    return max(1, int(latin_bytes / _LATIN_BYTES_PER_TOKEN + cjk_bytes / _CJK_BYTES_PER_TOKEN))


def extract_domain(url: str) -> str | None:
    """
    从URL中提取域名（包含协议）。

    Args:
        url (str): 要提取域名的URL。

    Returns:
        str | None: 提取出的域名（包含协议），如果解析失败或协议不支持则返回 None。
    """
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme in {"http", "https"} and parsed_url.netloc:
            return f"{parsed_url.scheme}://{parsed_url.netloc}".rstrip("/")
        return None  # 返回 None 表示 URL 格式不符合要求或协议不支持

    except ValueError:
        return None  # 如果 URL 格式无效，则返回 None


def detect_language(file_name: str | None, code: str) -> str:
    # TODO: 添加语言检测逻辑
    return ""


def filter_tag(el: Tag | PageElement | NavigableString | None) -> Tag | None:
    if el is None or not isinstance(el, Tag):
        return None
    return el


def get_attr_text(el: str | AttributeValueList | None) -> str:
    if el is None:
        return ""
    if isinstance(el, str):
        return el.strip()
    return " ".join(el).strip()


def get_og_url(soup: BeautifulSoup) -> str:
    og_tag = filter_tag(soup.find("meta", {"property": "og:url"}))
    return get_tag_text(og_tag, "content")


def get_og_site_name(soup: BeautifulSoup) -> str:
    og_tag = filter_tag(soup.find("meta", {"property": "og:site_name"}))
    return get_tag_text(og_tag, "content")


def get_og_description(soup: BeautifulSoup) -> str:
    og_tag = filter_tag(soup.find("meta", {"property": "og:description"}))
    return get_tag_text(og_tag, "content")


def get_canonical_url(soup: BeautifulSoup) -> str:
    canonical_tag = filter_tag(soup.find("link", {"rel": "canonical"}))
    return get_tag_text(canonical_tag, "href")


def is_matched_canonical(url: str, soup: BeautifulSoup) -> bool:
    canonical = get_canonical_url(soup)
    if not canonical:
        return False
    return canonical.startswith(url)


def get_og_title(soup: BeautifulSoup) -> str:
    og_tag = filter_tag(soup.find("meta", {"property": "og:title"}))
    return get_tag_text(og_tag, "content")


def get_tag_text(tag: Tag | None, attr: str) -> str:
    if tag is not None and tag.has_attr(attr):
        el = tag[attr]
        return get_attr_text(el)
    return ""


def get_title(soup: BeautifulSoup) -> str:
    title_tag = soup.title
    return title_tag.get_text(strip=True) if title_tag else ""


def convert_cookies_to_requests_dict(playwright_cookies: list[dict[str, Any]]) -> dict[str, str]:
    requests_cookies = {}
    for cookie in playwright_cookies:
        requests_cookies[cookie.get("name")] = cookie.get("value")
    return requests_cookies


# \u200b-\u200f: 零宽空格、各向异性连接符
# \u202a-\u202e: 方向控制符 (LRO, RLO 等)
# \ufeff: Byte Order Mark (BOM)
# \u2060-\u206f: 各种不可见连接符
_INVISIBLE_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\ufeff\u2060-\u206f]")


def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = _INVISIBLE_RE.sub("", text)
    return cleaned
