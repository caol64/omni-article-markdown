import re
from bs4 import BeautifulSoup, element, NavigableString


class HtmlMarkdownParser:

    ARTICLE_CONTAINER = [
        ("div", {"class": "main-content"}), # Freedium
        ("div", {"id": "page-content"}), # 公众号
        ("div", {"class": "post-content"}), # Hugo
        ("div", {"class": "article-content"}), # 头条
        ("div", {"class": "Post-RichText"}), # 知乎专栏
        ("article", None),
        ("main", None),
        ("body", None)
    ]

    TAGS_TO_CLEAN = [
        lambda el: el.name in ("script", "style", "link", "button", "footer", "header", "aside"),
    ]

    ATTRS_TO_CLEAN = [
        lambda el: 'style' in el.attrs and re.search(r'display\s*:\s*none', el.attrs['style'], re.IGNORECASE),
        lambda el: 'id' in el.attrs and el.attrs['id'] == 'meta_content', # 公众号
        lambda el: 'data-testid' in el.attrs, # Medium
        lambda el: 'class' in el.attrs and 'speechify-ignore' in el.attrs['class'] # Medium
    ]

    POST_HANDLER = [
        lambda el: el.replace("[|lb_bl|][|lb_bl|]", "[|lb_bl|]").replace("[|lb_bl|]", "\n\n").strip(), # 添加换行使文章更美观
        lambda el: re.sub(r"`\*\*(.*?)\*\*`", r"**`\1`**", el), # 纠正不规范格式 `**code**` 替换为 **`code`**
        lambda el: re.sub(r"`\*(.*?)\*`", r"*`\1`*", el), # 纠正不规范格式 `*code*` 替换为 *`code`*
    ]

    INLINE_ELEMENTS = [
        "span", "code", "li", "a", "strong", "em", "img"
    ]

    BLOCK_ELEMENTS = [
        "p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "blockquote", "pre", "picture", "hr", "figcaption"
    ]

    TRUSTED_ELEMENTS = INLINE_ELEMENTS + BLOCK_ELEMENTS

    def __init__(self, raw_html: str):
        self.raw_html = raw_html
        self.soup = BeautifulSoup(self.raw_html, "html5lib")
        self.title = None
        self.description = None

    def parse(self) -> tuple:
        self.extract_title()
        article = self.extract_article()
        if article:
            for element in article.find_all():
                # print(isinstance(element, NavigableString))
                if any(cond(element) for cond in HtmlMarkdownParser.TAGS_TO_CLEAN):
                    element.decompose()
                    continue
                if element.attrs:
                    if any(cond(element) for cond in HtmlMarkdownParser.ATTRS_TO_CLEAN):
                        element.decompose()
            # print(article)
            result = f"# {self.title}\n\n"
            if self.description:
                result += f"> {self.description}\n\n"
            markdown = self.process_children(article)
            for handler in HtmlMarkdownParser.POST_HANDLER:
                markdown = handler(markdown)
            result += markdown
            # print(result)
        return (self.title, result)

    def process_element(self, element: element, level: int = 0, is_strip: bool = True) -> str:
        parts = []
        if element.name == "br":
            parts.append("\n")
        elif element.name == "hr":
            parts.append("---")
        elif element.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            heading = self.process_children(element, is_strip=is_strip)
            parts.append(f"{'#' * int(element.name[1])} {heading}")
        elif element.name == "a":
            link = self.process_children(element, is_strip=is_strip).replace("[|lb_bl|]", "")
            if link:
                parts.append(f"[{link}]({element.get("href")})")
        elif element.name == "strong":
            parts.append(self.move_spaces(f"**{self.process_children(element, is_strip=is_strip)}**", "**"))
        elif element.name == "em":
            parts.append(self.move_spaces(f"*{self.process_children(element, is_strip=is_strip)}*", "*"))
        elif element.name == "ul" or element.name == "ol":
            parts.append(self.process_list(element, level))
        elif element.name == "img":
            src = element.get("src") or element.get("data-src")
            parts.append(f"![{element.get('alt', '')}]({src})" if src else "")
        elif element.name == "blockquote":
            blockquote = self.process_children(element, is_strip=is_strip)
            parts.append("\n".join(f"> {line}" for line in blockquote.split("[|lb_bl|]")))
        elif element.name == "pre":
            parts.append(self.process_codeblock(element))
        elif element.name == "code": # inner code
            code = self.process_children(element, is_strip=is_strip)
            if "\n" not in code:
                parts.append(f"`{code}`")
            else:
                parts.append(code)
        elif element.name == "picture":
            source_elements = element.find_all("source")
            img_element = element.find("img")
            if img_element and source_elements:
                src_set = source_elements[0]["srcset"]
                src = src_set.split()[0]
                if src:
                    parts.append(f"![{img_element.get('alt', '')}]({src})")
        elif element.name == "figcaption":
            figcaption = self.process_children(element, is_strip=is_strip)
            parts.append(f"*{figcaption}*")
        elif element.name == "table":
            parts.append(self.process_table(element))
        else:
            parts.append(self.process_children(element, is_strip=is_strip))
        result = ''.join(parts)
        if result and self.is_block_element(element):
            result = f"[|lb_bl|]{result}[|lb_bl|]"
        return result

    def process_children(self, element: element, level: int = 0, is_strip: bool = True) -> str:
        parts = []
        if element.children:
            for child in element.children:
                # print(bytes(str(child), 'utf-8'))
                if isinstance(child, NavigableString):
                    if element.name in HtmlMarkdownParser.TRUSTED_ELEMENTS:
                        parts.append(child.replace("<", "&lt;").replace(">", "&gt;") if is_strip else child)
                else:
                    parts.append(self.process_element(child, level, is_strip=is_strip))
        return ''.join(parts).strip() if is_strip else ''.join(parts)

    def process_list(self, element: element, level: int) -> str:
        indent = "    " * level
        li_list = element.find_all("li", recursive=False)
        is_ol = element.name == "ol"
        parts = [f"{indent}{f'{i + 1}.' if is_ol else '-'} {self.process_children(li, level+1).replace("[|lb_bl|]", "")}" for i, li in enumerate(li_list)]
        # print(level, parts)
        return f'\n{"\n".join(parts)}' if level > 0 else "\n".join(parts)

    def process_codeblock(self, element: element) -> str:
        code_element = element.find("code") or element
        code = self.process_children(code_element, is_strip=False).strip()
        if self.is_sequentially_increasing(code):
            return ''  # 如果代码块中的内容是连续递增的数字（极有可能是行号），则不输出代码块
        language = next((cls.split('-')[1] for cls in (code_element.get("class") or []) if cls.startswith("language-")), "")
        if not language:
            language = self.detect_language(code)
        return f"```{language}\n{code}\n```" if language else f"```\n{code}\n```"

    def process_table(self, element: element) -> str:
        if element.find("pre"):
            return self.process_children(element)
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

    def is_block_element(self, element: element) -> bool:
        return element.name in HtmlMarkdownParser.BLOCK_ELEMENTS

    def move_spaces(self, input_string: str, suffix: str) -> str:
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

    def extract_title(self):
        title_tag = self.soup.title
        title = title_tag.text.strip() if title_tag else None

        if title and title.endswith(" - Freedium"):
            h1 = self.soup.find("h1")
            self.title = h1.text.strip() if h1 else None

            h2 = self.soup.find("h2")
            self.description = h2.text.strip() if h2 else None

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

    def extract_article(self) -> element:
        for e in HtmlMarkdownParser.ARTICLE_CONTAINER:
            article = self._extract_article(e)
            if article:
                return article
        return None

    def _extract_article(self, template: tuple) -> element:
        if template[1] is not None:
            return self.soup.find(template[0], attrs=template[1])
        else:
            return self.soup.find(template[0])

    def is_sequentially_increasing(self, code: str) -> bool:
        try:
            # 解码并按换行符拆分
            numbers = [int(line.strip()) for line in code.split('\n') if line.strip()]
            # 检查是否递增
            return all(numbers[i] + 1 == numbers[i + 1] for i in range(len(numbers) - 1))
        except ValueError:
            return False  # 处理非数字情况

    def detect_language(self, code: str) -> str:
        # TODO: 添加语言检测逻辑
        return ''
