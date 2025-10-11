import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag, PageElement, AttributeValueList

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

BROWSER_TARGET_HOSTS = [
    "developer.apple.com/documentation/",
    "www.infoq.cn/",
]

def is_sequentially_increasing(code: str) -> bool:
    try:
        # 解码并按换行符拆分
        numbers = [int(line.strip()) for line in code.split("\n") if line.strip()]
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


def collapse_spaces(text) -> str:
    """
    将多个连续空格（包括换行和 Tab）折叠成一个空格。
    """
    return re.sub(r"\s+", " ", text)


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
    else:
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
