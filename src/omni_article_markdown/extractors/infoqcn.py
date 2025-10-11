from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import is_matched_canonical


class InfoQCNExtractor(Extractor):
    """
    www.infoq.cn
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return is_matched_canonical("https://www.infoq.cn", soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article-content-wrap"})
