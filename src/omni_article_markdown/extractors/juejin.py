from typing import override
from bs4 import BeautifulSoup

from ..utils import filter_tag
from ..extractor import Extractor, is_matched_canonical


class JuejinExtractor(Extractor):
    """
    juejin.cn
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return is_matched_canonical("https://juejin.cn/", soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"id": "article-root"})

    @override
    def extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = filter_tag(soup.find("h1", {"class": "article-title"}))
        return title_tag.get_text(strip=True) if title_tag else super().extract_title(soup)
