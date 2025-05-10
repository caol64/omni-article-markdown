import re
from urllib.parse import urlparse
from typing import Optional


class Constants:

    LB_SYMBOL = "[|lb_bl|]"

    ARTICLE_CONTAINERS = [
        ("div", {"class": "main-content"}), # Freedium
        ("div", {"id": "page-content"}), # 公众号
        ("div", {"class": "post-content"}), # Hugo
        ("div", {"class": "article-content"}), # 头条
        ("div", {"class": "Post-RichText"}), # 知乎专栏
        ("div", {"id": "postBody"}), # quantamagazine
        ("article", None),
        ("main", None),
        ("body", None)
    ]

    TAGS_TO_CLEAN = [
        lambda el: el.name in ("style", "link", "button", "footer", "header", "aside"),
        lambda el: el.name == "script" and "src" not in el.attrs,
        lambda el: el.name == "script" and "src" in el.attrs and not el.attrs["src"].startswith("https://gist.github.com"),
    ]

    ATTRS_TO_CLEAN = [
        lambda el: 'style' in el.attrs and re.search(r'display\s*:\s*none', el.attrs['style'], re.IGNORECASE),
        lambda el: 'id' in el.attrs and el.attrs['id'] == 'meta_content', # 公众号
        lambda el: 'data-testid' in el.attrs, # Medium
        lambda el: 'class' in el.attrs and 'speechify-ignore' in el.attrs['class'], # Medium
        lambda el: 'hidden' in el.attrs,
        lambda el: 'class' in el.attrs and 'katex-html' in el.attrs['class'], # katex
    ]

    POST_HANDLERS = [
        lambda el: el.replace(f"{Constants.LB_SYMBOL}{Constants.LB_SYMBOL}", Constants.LB_SYMBOL).replace(Constants.LB_SYMBOL, "\n\n").strip(), # 添加换行使文章更美观
        lambda el: re.sub(r"`\*\*(.*?)\*\*`", r"**`\1`**", el), # 纠正不规范格式 `**code**` 替换为 **`code`**
        lambda el: re.sub(r"`\*(.*?)\*`", r"*`\1`*", el), # 纠正不规范格式 `*code*` 替换为 *`code`*
        lambda el: re.sub(r"`\s*\[([^\]]+)\]\(([^)]+)\)\s*`", r"[`\1`](\2)", el) # 纠正不规范格式 `[code](url)` 替换为 [`code`](url)
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