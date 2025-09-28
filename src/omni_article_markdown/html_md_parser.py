import re
from bs4 import element, NavigableString
import requests

from .extractor import Article
from .utils import (
    Constants,
    is_sequentially_increasing,
    is_block_element,
    move_spaces,
    detect_language,
    collapse_spaces,
    extract_domain,
    is_pure_block_children,
)

class HtmlMarkdownParser:

    def __init__(self, article: Article, og_url: str = None):
        self.article = article
        self.url = og_url

    def parse(self) -> tuple:
        if self.article:
            # print(article)
            markdown = self._process_children(self.article.body)
            for handler in Constants.POST_HANDLERS:
                markdown = handler(markdown)
            if not self.article.description or self.article.description in markdown:
                description = ""
            else:
                description = f"> {self.article.description}\n\n"
            result = f"# {self.article.title}\n\n{description}{markdown}"
            # print(result)
            return (self.article.title, result)
        return (None, None)

    def _process_element(self, element: element.Tag, level: int = 0, is_pre: bool = False) -> str:
        parts = []
        if element.name == "br":
            parts.append(Constants.LB_SYMBOL)
        elif element.name == "hr":
            parts.append("---")
        elif element.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            heading = self._process_children(element, level, is_pre=is_pre)
            parts.append(f"{'#' * int(element.name[1])} {heading}")
        elif element.name == "a":
            link = self._process_children(element, level, is_pre=is_pre).replace(Constants.LB_SYMBOL, "")
            if link:
                parts.append(f"[{link}]({element.get("href")})")
        elif element.name == "strong" or element.name == "b":
            parts.append(move_spaces(f"**{self._process_children(element, level, is_pre=is_pre)}**", "**"))
        elif element.name == "em" or element.name == "i":
            parts.append(move_spaces(f"*{self._process_children(element, level, is_pre=is_pre)}*", "*"))
        elif element.name == "ul" or element.name == "ol":
            parts.append(self._process_list(element, level))
        elif element.name == "img":
            src = element.get("data-src") or element.get("src")
            parts.append(self._process_image(src, element.get("alt", "")))
        elif element.name == "blockquote":
            blockquote = self._process_children(element, level, is_pre=is_pre)
            if blockquote.startswith(Constants.LB_SYMBOL):
                blockquote = blockquote.removeprefix(Constants.LB_SYMBOL)
            if blockquote.endswith(Constants.LB_SYMBOL):
                blockquote = blockquote.removesuffix(Constants.LB_SYMBOL)
            parts.append("\n".join(f"> {line}" for line in blockquote.split(Constants.LB_SYMBOL)))
        elif element.name == "pre":
            parts.append(self._process_codeblock(element, level))
        elif element.name == "code": # inner code
            code = self._process_children(element, level, is_pre=is_pre)
            if Constants.LB_SYMBOL not in code:
                parts.append(f"`{code}`")
            else:
                parts.append(code)
        elif element.name == "picture":
            source_elements = element.find_all("source")
            img_element = element.find("img")
            if img_element and source_elements:
                src_set = source_elements[0]["srcset"]
                src = src_set.split()[0]
                parts.append(self._process_image(src, img_element.get("alt", "")))
        elif element.name == "figcaption":
            figcaption = self._process_children(element, level, is_pre=is_pre).replace(Constants.LB_SYMBOL, "\n").strip()
            figcaptions = figcaption.replace("\n\n", "\n").split("\n")
            parts.append("\n".join([f"*{caption}*" for caption in figcaptions]))
        elif element.name == "table":
            parts.append(self._process_table(element, level))
        elif element.name == "math": # 处理latex公式
            semantics = element.find("semantics")
            if semantics:
                tex = semantics.find(attrs={'encoding': 'application/x-tex'})
                if tex:
                    parts.append(f"$$ {tex.text} $$")
        elif element.name == "script": # 处理github gist
            parts.append(self._process_gist(element))
        else:
            parts.append(self._process_children(element, level, is_pre=is_pre))
        result = ''.join(parts)
        if result and is_block_element(element.name):
            if not is_pure_block_children(element):
                result = f"{Constants.LB_SYMBOL}{result}{Constants.LB_SYMBOL}"
        return result

    def _process_children(self, element: element.Tag, level: int = 0, is_pre: bool = False) -> str:
        parts = []
        if element.children:
            # new_level = level + 1 if element.name in Constants.TRUSTED_ELEMENTS else level
            for child in element.children:
                if isinstance(child, NavigableString):
                    if is_pre:
                        parts.append(child)
                    else:
                        result = collapse_spaces(child).replace("<", "&lt;").replace(">", "&gt;")
                        if result.strip():
                            parts.append(result)
                        # print(element.name, level, result)
                else:
                    result = self._process_element(child, level, is_pre=is_pre)
                    if is_pre or len(result.replace(Constants.LB_SYMBOL, "")) != 0:
                        parts.append(result)
        return ''.join(parts) if is_pre or level > 0 else ''.join(parts).strip()

    def _process_list(self, element: element.Tag, level: int) -> str:
        indent = "  " * level
        child_list = element.find_all(recursive=False)
        is_ol = element.name == "ol"
        parts = []
        for i, child in enumerate(child_list):
            if child.name == "li":
                content = self._process_children(child, level).replace(Constants.LB_SYMBOL, "").strip()
                if content:  # 忽略空内容
                    prefix = f"{i + 1}." if is_ol else "-"
                    parts.append(f"{indent}{prefix} {content}")
            elif child.name == "ul" or child.name == "ol":
                content = self._process_element(child, level + 1)
                if content:  # 忽略空内容
                    parts.append(f"{content.replace(Constants.LB_SYMBOL, "")}")
        if not parts:
            return ""  # 所有内容都为空则返回空字符串
        return "\n".join(parts)

    def _process_codeblock(self, element: element.Tag, level: int) -> str:
        # 找出所有 code 标签（可能为 0 个、1 个或多个）
        code_elements = element.find_all("code") or [element]

        # 处理每一个 code 标签并拼接
        code_parts = [
            self._process_children(code_el, level, is_pre=True).replace(Constants.LB_SYMBOL, "\n")
            for code_el in code_elements
        ]
        code = "\n".join(code_parts).strip()

        if is_sequentially_increasing(code):
            return ''  # 忽略行号

        # 尝试提取语言：从第一个 code 标签的 class 中提取 language
        first_code_el = code_elements[0]
        language = next(
            (cls.split('-')[1] for cls in (first_code_el.get("class") or []) if cls.startswith("language-")),
            ""
        )
        if not language:
            language = detect_language(None, code)
        return f"```{language}\n{code}\n```" if language else f"```\n{code}\n```"

    def _process_table(self, element: element.Tag, level: int) -> str:
        if element.find("pre"):
            return self._process_children(element, level)
        # 获取所有行，包括 thead 和 tbody
        rows = element.find_all("tr")
        # 解析表头（如果有）
        headers = []
        if rows and rows[0].find_all("th"):
            headers = [th.get_text(strip=True) for th in rows.pop(0).find_all("th")]
        # 解析表身
        body = [[td.get_text(strip=True) for td in row.find_all("td")] for row in rows]
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

    def _process_image(self, src: str, alt: str) -> str:
        if src:
            if src.startswith("/") and self.url:
                domain = extract_domain(self.url)
                src = f"{domain}{src}"
            return f"![{alt}]({src})"
        return ""

    def _process_gist(self, element: element.Tag) -> str:
        src = element.attrs["src"]
        pattern = r"/([0-9a-f]+)(?:\.js)?$"
        match = re.search(pattern, src)
        if match:
            gist_id = match.group(1)
        else:
            return ""
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
