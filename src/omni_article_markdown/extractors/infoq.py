from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor, is_matched_canonical


class InfoQExtractor(Extractor):
    """
    www.infoq.com
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return is_matched_canonical("https://www.infoq.com", soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article__data"})
