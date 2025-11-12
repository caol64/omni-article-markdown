from typing import override

from bs4 import BeautifulSoup

from ..extractor import Extractor


class HugoExtractor(Extractor):
    """
    Hugo博客
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return False

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "post-content"})
