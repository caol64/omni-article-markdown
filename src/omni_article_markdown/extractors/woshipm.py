from typing import override

from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import get_og_url


class WoShiPMExtractor(Extractor):
    """
    人人都是产品经理
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_url(soup).startswith("https://www.woshipm.com")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article--content"})
