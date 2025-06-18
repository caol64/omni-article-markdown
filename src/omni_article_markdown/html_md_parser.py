import re
from bs4 import BeautifulSoup, element, NavigableString
import requests
import importlib
import pkgutil
from pathlib import Path

from .extractor import Extractor
from .utils import (
    Constants,
    is_sequentially_increasing,
    is_block_element,
    move_spaces,
    detect_language,
    collapse_spaces,
    extract_domain,
)

class HtmlMarkdownParser:

    def __init__(self, raw_html: str):
        self.raw_html = raw_html
        self.soup = BeautifulSoup(self.raw_html, "html5lib")
        self.extractors = self.load_extractors()
        self.title = None
        self.description = None
        self.url = None

    def parse(self) -> tuple:
        article = self.extract_article()
        if article:
            self.extract_title_and_description(article)
            for element in article.find_all():
                # print(isinstance(element, NavigableString))
                if any(cond(element) for cond in Constants.TAGS_TO_CLEAN):
                    element.decompose()
                    continue
                if element.attrs:
                    if any(cond(element) for cond in Constants.ATTRS_TO_CLEAN):
                        element.decompose()
            # print(article)
            result = f"# {self.title}\n\n"
            if self.description:
                result += f"> {self.description}\n\n"
            markdown = self.process_children(article)
            for handler in Constants.POST_HANDLERS:
                markdown = handler(markdown)
            result += markdown
            # print(result)
            return (self.title, result)
        return (None, None)

    def process_element(self, element: element, level: int = 0, is_pre: bool = False) -> str:
        parts = []
        if element.name == "br":
            parts.append(Constants.LB_SYMBOL)
        elif element.name == "hr":
            parts.append("---")
        elif element.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            heading = self.process_children(element, level, is_pre=is_pre)
            parts.append(f"{'#' * int(element.name[1])} {heading}")
        elif element.name == "a":
            link = self.process_children(element, level, is_pre=is_pre).replace(Constants.LB_SYMBOL, "")
            if link:
                parts.append(f"[{link}]({element.get("href")})")
        elif element.name == "strong" or element.name == "b":
            parts.append(move_spaces(f"**{self.process_children(element, level, is_pre=is_pre)}**", "**"))
        elif element.name == "em" or element.name == "i":
            parts.append(move_spaces(f"*{self.process_children(element, level, is_pre=is_pre)}*", "*"))
        elif element.name == "ul" or element.name == "ol":
            parts.append(self.process_list(element, level))
        elif element.name == "img":
            src = element.get("data-src") or element.get("src")
            parts.append(self.process_image(src, element.get("alt", "")))
        elif element.name == "blockquote":
            blockquote = self.process_children(element, level, is_pre=is_pre)
            if blockquote.startswith(Constants.LB_SYMBOL):
                blockquote = blockquote.removeprefix(Constants.LB_SYMBOL)
            if blockquote.endswith(Constants.LB_SYMBOL):
                blockquote = blockquote.removesuffix(Constants.LB_SYMBOL)
            parts.append("\n".join(f"> {line}" for line in blockquote.split(Constants.LB_SYMBOL)))
        elif element.name == "pre":
            parts.append(self.process_codeblock(element, level))
        elif element.name == "code": # inner code
            code = self.process_children(element, level, is_pre=is_pre)
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
                parts.append(self.process_image(src, img_element.get("alt", "")))
        elif element.name == "figcaption":
            figcaption = self.process_children(element, level, is_pre=is_pre).replace(Constants.LB_SYMBOL, "\n").strip()
            figcaptions = figcaption.replace("\n\n", "\n").split("\n")
            parts.append("\n".join([f"*{caption}*" for caption in figcaptions]))
        elif element.name == "table":
            parts.append(self.process_table(element, level))
        elif element.name == "math": # 处理latex公式
            semantics = element.find("semantics")
            if semantics:
                tex = semantics.find(attrs={'encoding': 'application/x-tex'})
                if tex:
                    parts.append(f"$$ {tex.text} $$")
        elif element.name == "script": # 处理github gist
            parts.append(self.process_gist(element))
        else:
            parts.append(self.process_children(element, level, is_pre=is_pre))
        result = ''.join(parts)
        if result and is_block_element(element.name):
            result = f"{Constants.LB_SYMBOL}{result}{Constants.LB_SYMBOL}"
        return result

    def process_children(self, element: element, level: int = 0, is_pre: bool = False) -> str:
        parts = []
        if element.children:
            new_level = level + 1 if element.name in Constants.TRUSTED_ELEMENTS else level
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
                    parts.append(self.process_element(child, new_level, is_pre=is_pre))
        return ''.join(parts) if is_pre or level > 0 else ''.join(parts).strip()

    def process_list(self, element: element, level: int) -> str:
        indent = "    " * level
        li_list = element.find_all("li", recursive=False)
        is_ol = element.name == "ol"
        parts = [f"{indent}{f'{i + 1}.' if is_ol else '-'} {self.process_children(li, level).replace(Constants.LB_SYMBOL, "")}" for i, li in enumerate(li_list)]
        # print(level, parts)
        return f'\n{"\n".join(parts)}' if level > 0 else "\n".join(parts)

    def process_codeblock(self, element: element, level: int) -> str:
        code_element = element.find("code") or element
        code = self.process_children(code_element, level, is_pre=True).replace(Constants.LB_SYMBOL, "\n")
        if is_sequentially_increasing(code):
            return ''  # 如果代码块中的内容是连续递增的数字（极有可能是行号），则不输出代码块
        language = next((cls.split('-')[1] for cls in (code_element.get("class") or []) if cls.startswith("language-")), "")
        if not language:
            language = detect_language(None, code)
        return f"```{language}\n{code}\n```" if language else f"```\n{code}\n```"

    def process_table(self, element: element, level: int) -> str:
        if element.find("pre"):
            return self.process_children(element, level)
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
            headers = ["Column " + str(i+1) for i in range(len(body[0]))]
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

    def process_image(self, src: str, alt: str) -> str:
        if src:
            if src.startswith("/") and self.url:
                domain = extract_domain(self.url)
                src = f"{domain}{src}"
            return f"![{alt}]({src})"
        return ""

    def process_gist(self, element: element) -> str:
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

    def extract_title_and_description(self, article: element):
        title_tag = self.soup.title
        title = title_tag.text.strip() if title_tag else None
        if title and title.endswith(" - Freedium"):
            h1 = self.soup.find("h1")
            self.title = h1.text.strip() if h1 else None
            h2 = self.soup.find("h2")
            self.description = h2.text.strip() if h2 else None
        h1 = article.find("h1", {"class": "wp-block-post-title"})
        if h1:
            self.title = h1.text.strip() if h1 else None
            h1.decompose()
        # 如果 title 仍为空，尝试获取 og:title
        if not self.title:
            og_title = self.soup.find("meta", {"property": "og:title"})
            self.title = og_title["content"].strip() if og_title and "content" in og_title.attrs else title
        # 确保 title 不为 None
        self.title = self.title or "Untitled"
        # 确保 description 不为 None，尝试获取 og:description
        if not self.description:
            og_desc = self.soup.find("meta", {"property": "og:description"})
            self.description = og_desc["content"].strip() if og_desc and "content" in og_desc.attrs else None
        og_url = self.soup.find("meta", {"property": "og:url"})
        self.url = og_url["content"].strip() if og_url and "content" in og_url.attrs else None

    def extract_article(self) -> element:
        article_containers = []
        for extract in self.extractors:
            article_containers.append(extract.extract())
        article_containers.extend(Constants.ARTICLE_CONTAINERS)
        for e in article_containers:
            article = self._extract_article(e)
            if article:
                return article
        return None

    def _extract_article(self, template: tuple) -> element:
        if template[1] is not None:
            return self.soup.find(template[0], attrs=template[1])
        else:
            return self.soup.find(template[0])

    def load_extractors(self, package_name="extractors") -> list[Extractor]:
        extractors_package = Path(__file__).parent / package_name
        extractors = []
        for loader, module_name, is_pkg in pkgutil.iter_modules([extractors_package.resolve()]):
            module = importlib.import_module(f"omni_article_markdown.{package_name}.{module_name}")
            for attr in dir(module):
                cls = getattr(module, attr)
                if isinstance(cls, type) and issubclass(cls, Extractor) and cls is not Extractor:
                    extractors.append(cls())
        return extractors
