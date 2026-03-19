import re
from typing import override

from bs4 import BeautifulSoup

from ..extractor import Article, Extractor


class FeishuExtractor(Extractor):
    """
    飞书文档
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        # 通过飞书文档特有的 class 来识别
        wiki_box = soup.find("div", class_="wikiSSRBox")
        suite_doc = soup.find("div", class_="suite-doc")
        return wiki_box is not None and suite_doc is not None

    @override
    def article_container(self) -> tuple:
        # 飞书文档的内容在 render-unit-wrapper 中
        return ("div", {"class": "render-unit-wrapper"})

    @override
    def extract_title(self, soup: BeautifulSoup) -> str:
        # 优先从 SERVER_DATA 中提取标题
        for script in soup.find_all("script"):
            if script.string and "window.SERVER_DATA" in script.string:
                match = re.search(r'"title"\s*:\s*"([^"]+)"', script.string)
                if match:
                    return match.group(1)

        # 其次从 page-block-header 中提取
        header = soup.find("div", class_="page-block-header__custom_icon")
        if header:
            return header.get_text(strip=True)

        # 最后使用默认的 title 标签
        return super().extract_title(soup)

    @override
    def pre_handle_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        预处理飞书文档的 HTML，清理不需要的元素并转换特殊标签
        """
        # 1. 将 heading 块转换为标准的 h1, h2, h3 等标签
        for block_type, tag_name in [
            ("heading1", "h1"),
            ("heading2", "h2"),
            ("heading3", "h3"),
            ("heading4", "h4"),
            ("heading5", "h5"),
            ("heading6", "h6"),
        ]:
            for heading_block in soup.find_all("div", {"data-block-type": block_type}):
                # 创建新的 heading 标签
                new_tag = soup.new_tag(tag_name)
                # 提取文本内容
                text = heading_block.get_text(strip=True)
                # 移除末尾的特殊字符（飞书文档的特殊格式）
                text = text.rstrip("\u200b\u200c\u200d\ufeff")
                new_tag.string = text
                # 替换原元素
                heading_block.replace_with(new_tag)

        # 2. 移除所有图片块中的占位符和无关内容
        for img_block in soup.find_all("div", class_="docx-image-block"):
            # 移除图片块中的非图片元素（如 figcaption 等）
            for child in img_block.find_all(recursive=True):
                if child.name not in ["img"]:
                    # 保留可能有实际内容的元素
                    if child.get_text(strip=True):
                        continue
                    child.decompose()

        # 3. 处理引用块
        for quote_container in soup.find_all("div", {"data-block-type": "quote_container"}):
            # 将引用块转换为 blockquote 标签
            new_tag = soup.new_tag("blockquote")
            # 提取文本内容
            text = quote_container.get_text(strip=True)
            new_tag.string = text
            quote_container.replace_with(new_tag)

        # 4. 处理代码块
        for code_block in soup.find_all("div", {"data-block-type": "code"}):
            # 将代码块转换为 pre 标签
            new_tag = soup.new_tag("pre")
            code_tag = soup.new_tag("code")
            text = code_block.get_text(strip=True)
            code_tag.string = text
            new_tag.append(code_tag)
            code_block.replace_with(new_tag)

        return soup

    @override
    def extract_article(self, soup: BeautifulSoup) -> Article | None:
        # 飞书文档有特殊的内容结构，直接处理
        wrapper = soup.find("div", class_="render-unit-wrapper")
        if not wrapper:
            return None

        title = self.extract_title(soup)
        return Article(title=title, url=None, description=None, body=wrapper)
