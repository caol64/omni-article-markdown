import re
from typing import Callable
from urllib.parse import urljoin
from bs4.element import NavigableString, Tag
import requests

from .extractor import Article
from .utils import (
    filter_tag,
    get_attr_text,
    is_sequentially_increasing,
    move_spaces,
    detect_language,
    collapse_spaces,
)

LB_SYMBOL = "[|lb_bl|]"

POST_HANDLERS: list[Callable[[str], str]] = [
    # 添加换行使文章更美观
    lambda el: re.sub(f"(?:{re.escape(LB_SYMBOL)})+", LB_SYMBOL, el).replace(LB_SYMBOL, "\n\n").strip(),
    # 纠正不规范格式 `**code**` 替换为 **`code`**
    lambda el: re.sub(r"`\*\*(.*?)\*\*`", r"**`\1`**", el),
    # 纠正不规范格式 `*code*` 替换为 *`code`*
    lambda el: re.sub(r"`\*(.*?)\*`", r"*`\1`*", el),
    # 纠正不规范格式 `[code](url)` 替换为 [`code`](url)
    lambda el: re.sub(r"`\s*\[([^\]]+)\]\(([^)]+)\)\s*`", r"[`\1`](\2)", el),
    # 将 \( ... \) 替换为 $ ... $
    lambda el: re.sub(r"\\\((.+?)\\\)", r"$\1$", el),
    # 将 \[ ... \] 替换为 $$ ... $$
    lambda el: re.sub(r"\\\[(.+?)\\\]", r"$$\1$$", el),
]

INLINE_ELEMENTS = ["span", "code", "li", "a", "strong", "em", "b", "i"]

BLOCK_ELEMENTS = [
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "blockquote",
    "pre",
    "img",
    "picture",
    "hr",
    "figcaption",
    "table",
    "section",
]

TRUSTED_ELEMENTS = INLINE_ELEMENTS + BLOCK_ELEMENTS


class HtmlMarkdownParser:
    def __init__(self, article: Article):
        self.article = article

    def parse(self) -> tuple[str, str]:
        if isinstance(self.article.body, str):
            markdown = self.article.body
        else:
            markdown = self._process_children(self.article.body)
        for handler in POST_HANDLERS:
            markdown = handler(markdown)
        if not self.article.description or self.article.description in markdown:
            description = ""
        else:
            description = f"> {self.article.description}\n\n"
        result = f"# {self.article.title}\n\n{description}{markdown}"
        # print(result)
        return (self.article.title, result)

    def _process_element(self, element: Tag, level: int = 0, is_pre: bool = False) -> str:
        parts = []
        tag = element.name
        match tag:
            case "br":
                parts.append(LB_SYMBOL)
            case "hr":
                parts.append("---")
            case "h1" | "h2" | "h3" | "h4" | "h5" | "h6":
                heading = self._process_children(element, level, is_pre=is_pre)
                parts.append(f"{'#' * int(element.name[1])} {heading}")
            case "a":
                link = self._process_children(element, level, is_pre=is_pre).replace(LB_SYMBOL, "")
                if link:
                    parts.append(f"[{link}]({element.get('href')})")
            case "strong" | "b":
                parts.append(move_spaces(f"**{self._process_children(element, level, is_pre=is_pre)}**", "**"))
            case "em" | "i":
                parts.append(move_spaces(f"*{self._process_children(element, level, is_pre=is_pre)}*", "*"))
            case "ul" | "ol":
                parts.append(self._process_list(element, level))
            case "img":
                parts.append(self._process_image(element, None))
            case "blockquote":
                blockquote = self._process_children(element, level, is_pre=is_pre)
                if blockquote.startswith(LB_SYMBOL):
                    blockquote = blockquote.removeprefix(LB_SYMBOL)
                if blockquote.endswith(LB_SYMBOL):
                    blockquote = blockquote.removesuffix(LB_SYMBOL)
                parts.append("\n".join(f"> {line}" for line in blockquote.split(LB_SYMBOL)))
            case "pre":
                parts.append(self._process_codeblock(element, level))
            case "code":  # inner code
                code = self._process_children(element, level, is_pre=is_pre)
                if LB_SYMBOL not in code:
                    parts.append(f"`{code}`")
                else:
                    parts.append(code)
            case "picture":
                source_elements = element.find_all("source")
                img_element = filter_tag(element.find("img"))
                if img_element and source_elements:
                    el = source_elements[0]
                    src_el = filter_tag(el)
                    if src_el:
                        parts.append(self._process_image(img_element, src_el))
                elif img_element:
                    parts.append(self._process_image(img_element, None))
            case "figcaption":
                figcaption = self._process_children(element, level, is_pre=is_pre).replace(LB_SYMBOL, "\n").strip()
                figcaptions = figcaption.replace("\n\n", "\n").split("\n")
                parts.append("\n".join([f"*{caption}*" for caption in figcaptions]))
            case "table":
                parts.append(self._process_table(element, level))
            case "math":  # 处理latex公式
                semantics = filter_tag(element.find("semantics"))
                if semantics:
                    tex = filter_tag(semantics.find(attrs={"encoding": "application/x-tex"}))
                    if tex:
                        parts.append(f"$$ {tex.text} $$")
            case "script":  # 处理github gist
                parts.append(self._process_gist(element))
            case _:
                parts.append(self._process_children(element, level, is_pre=is_pre))
        result = "".join(parts)
        if result and is_block_element(element.name):
            if not element.children or not is_pure_block_children(element):
                result = f"{LB_SYMBOL}{result}{LB_SYMBOL}"
        return result

    def _process_children(self, element: Tag, level: int = 0, is_pre: bool = False) -> str:
        parts = []
        if element.children:
            # new_level = level + 1 if element.name in HtmlMarkdownParser.TRUSTED_ELEMENTS else level
            for child in element.children:
                if isinstance(child, NavigableString):
                    if is_pre:
                        parts.append(child)
                    else:
                        result = collapse_spaces(child).replace("<", "&lt;").replace(">", "&gt;")
                        if result.strip():
                            parts.append(result)
                        # print(element.name, level, result)
                elif isinstance(child, Tag):
                    result = self._process_element(child, level, is_pre=is_pre)
                    if is_pre:
                        parts.append(result)
                    elif result.strip():
                        parts.append(result.strip())
        return "".join(parts) if is_pre or level > 0 else "".join(parts).strip()

    def _process_list(self, element: Tag, level: int) -> str:
        indent = "  " * level
        child_list = element.find_all(recursive=False)
        is_ol = element.name == "ol"
        parts = []
        for i, child in enumerate(child_list):
            child = filter_tag(child)
            if child:
                if child.name == "li":
                    content = self._process_children(child, level).replace(LB_SYMBOL, "\n").strip()
                    if content:  # 忽略空内容
                        prefix = f"{i + 1}." if is_ol else "-"
                        parts.append(f"{indent}{prefix} {content}")
                elif child.name == "ul" or child.name == "ol":
                    content = self._process_element(child, level + 1)
                    if content:  # 忽略空内容
                        parts.append(f"{content.replace(LB_SYMBOL, '\n')}")
        if not parts:
            return ""  # 所有内容都为空则返回空字符串
        return "\n".join(parts)

    def _process_codeblock(self, element: Tag, level: int) -> str:
        # 找出所有 code 标签（可能为 0 个、1 个或多个）
        code_elements = element.find_all("code") or [element]

        # 处理每一个 code 标签并拼接
        code_parts = [
            self._process_children(code_el, level, is_pre=True).replace(LB_SYMBOL, "\n")
            for code_el in code_elements
            if isinstance(code_el, Tag)
        ]
        code = "\n".join(code_parts).strip()

        if is_sequentially_increasing(code):
            return ""  # 忽略行号

        # 尝试提取语言：从第一个 code 标签的 class 中提取 language
        first_code_el = code_elements[0]
        language = (
            next((cls.split("-")[1] for cls in (first_code_el.get("class") or []) if cls.startswith("language-")), "")
            if isinstance(first_code_el, Tag)
            else ""
        )
        if not language:
            language = detect_language(None, code)
        return f"```{language}\n{code}\n```" if language else f"```\n{code}\n```"

    def _process_table(self, element: Tag, level: int) -> str:
        if element.find("pre"):
            return self._process_children(element, level)
        # 获取所有行，包括 thead 和 tbody
        rows = element.find_all("tr")
        if not rows:
            return ""
        # 解析表头（如果有）
        headers = []
        first_row = filter_tag(rows.pop(0))
        if first_row and first_row.find("th"):
            headers = [th.get_text(strip=True) for th in first_row.find_all("th")]
        # 解析表身
        body = [[td.get_text(strip=True) for td in row.find_all("td")] for row in rows if isinstance(row, Tag)]
        # 处理缺失的表头
        if not headers and body:
            headers = body.pop(0)
        # 统一列数
        col_count = max(len(headers), max((len(row) for row in body), default=0))
        headers += [""] * (col_count - len(headers))
        for row in body:
            row += [""] * (col_count - len(row))
        # 生成 Markdown 表格
        markdown_table = []
        markdown_table.append("| " + " | ".join(headers) + " |")
        markdown_table.append("|-" + "-|-".join(["-" * len(h) for h in headers]) + "-|")
        for row in body:
            markdown_table.append("| " + " | ".join(row) + " |")
        return "\n".join(markdown_table)

    def _process_image(self, element: Tag, source: Tag | None) -> str:
        src = (
            get_attr_text(element.attrs.get("src"))
            if source is None
            else get_attr_text(source.attrs.get("srcset")).split()[0]
        )
        alt = get_attr_text(element.attrs.get("alt"))
        if src:
            if not src.startswith("http") and self.article.url:
                src = urljoin(self.article.url, src)
            return f"![{alt}]({src})"
        return ""

    def _process_gist(self, element: Tag) -> str:
        src = get_attr_text(element.attrs.get("src"))
        pattern = r"/([0-9a-f]+)(?:\.js)?$"
        match = re.search(pattern, src)
        if match:
            gist_id = match.group(1)
            url = f"https://api.github.com/gists/{gist_id}"
            response = requests.get(url)
            response.encoding = "utf-8"
            if response.status_code == 200:
                data = response.json()
                gists = []
                for filename, info in data["files"].items():
                    code = info["content"]
                    language = detect_language(filename, code)
                    gists.append(f"```{language}\n{code}\n```")
                return "\n\n".join(gists)
            else:
                print(f"Fetch gist error: {response.status_code}")
        return ""


def is_block_element(element_name: str) -> bool:
    return element_name in BLOCK_ELEMENTS


def is_pure_block_children(element: Tag) -> bool:
    for child in element.children:
        if isinstance(child, NavigableString):
            if child.strip():  # 有非空文本
                return False
        elif isinstance(child, Tag) and not is_block_element(child.name):
            return False
    return True
