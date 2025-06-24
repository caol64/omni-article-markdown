import re
from urllib.parse import urlparse
from typing import Optional
from bs4 import BeautifulSoup, element


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
    "Upgrade-Insecure-Requests": "1"
}

class Constants:

    LB_SYMBOL = "[|lb_bl|]"

    ARTICLE_CONTAINERS = [
        ("article", None),
        ("main", None),
        ("body", None)
    ]

    TAGS_TO_CLEAN = [
        lambda el: el.name in ("style", "link", "button", "footer", "header", "aside", "script"),
        # lambda el: el.name == "script" and "src" not in el.attrs,
        # lambda el: el.name == "script" and "src" in el.attrs and not el.attrs["src"].startswith("https://gist.github.com"),
    ]

    ATTRS_TO_CLEAN = [
        lambda el: 'style' in el.attrs and re.search(r'display\s*:\s*none', el.attrs['style'], re.IGNORECASE),
        lambda el: 'hidden' in el.attrs,
        lambda el: 'class' in el.attrs and 'katex-html' in el.attrs['class'], # katex
    ]

    POST_HANDLERS = [
        lambda el: el.replace(f"{Constants.LB_SYMBOL}{Constants.LB_SYMBOL}", Constants.LB_SYMBOL).replace(Constants.LB_SYMBOL, "\n\n").strip(), # 添加换行使文章更美观
        lambda el: re.sub(r"`\*\*(.*?)\*\*`", r"**`\1`**", el), # 纠正不规范格式 `**code**` 替换为 **`code`**
        lambda el: re.sub(r"`\*(.*?)\*`", r"*`\1`*", el), # 纠正不规范格式 `*code*` 替换为 *`code`*
        lambda el: re.sub(r"`\s*\[([^\]]+)\]\(([^)]+)\)\s*`", r"[`\1`](\2)", el), # 纠正不规范格式 `[code](url)` 替换为 [`code`](url)
        lambda el: re.sub(r"\\\((.+?)\\\)", r"$\1$", el), # 将 \( ... \) 替换为 $ ... $
        lambda el: re.sub(r"\\\[(.+?)\\\]", r"$$\1$$", el), # 将 \[ ... \] 替换为 $$ ... $$
    ]

    INLINE_ELEMENTS = [
        "span", "code", "li", "a", "strong", "em", "img", "b", "i"
    ]

    BLOCK_ELEMENTS = [
        "p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "blockquote", "pre", "picture", "hr", "figcaption"
    ]

    TRUSTED_ELEMENTS = INLINE_ELEMENTS + BLOCK_ELEMENTS


def is_sequentially_increasing(code: str) -> bool:
    try:
        # 解码并按换行符拆分
        numbers = [int(line.strip()) for line in code.split('\n') if line.strip()]
        # 检查是否递增
        return all(numbers[i] + 1 == numbers[i + 1] for i in range(len(numbers) - 1))
    except ValueError:
        return False  # 处理非数字情况

def is_block_element(element_name: str) -> bool:
    return element_name in Constants.BLOCK_ELEMENTS

def move_spaces(input_string: str, suffix: str) -> str:
    # 使用正则表达式匹配以指定的suffix结尾，且suffix之前有空格的情况
    escaped_suffix = re.escape(suffix)  # 处理正则中的特殊字符
    pattern = rf'(.*?)\s+({escaped_suffix})$'
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
    return re.sub(r'\s+', ' ', text)

def extract_domain(url: str) -> Optional[str]:
    """
    从URL中提取域名（包含协议）。

    Args:
        url (str): 要提取域名的URL。

    Returns:
        Optional[str]: 提取出的域名（包含协议），如果解析失败或协议不支持则返回 None。
    """
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme in {"http", "https"} and parsed_url.netloc:
            return f"{parsed_url.scheme}://{parsed_url.netloc}".rstrip('/')
        return None  # 返回 None 表示 URL 格式不符合要求或协议不支持

    except ValueError:
        return None  # 如果 URL 格式无效，则返回 None

def detect_language(file_name: str, code: str) -> str:
    # TODO: 添加语言检测逻辑
    return ''


def extract_article_from_soup(soup: BeautifulSoup, template: tuple) -> element.Tag:
    if template[1] is not None:
        return soup.find(template[0], attrs=template[1])
    else:
        return soup.find(template[0])
