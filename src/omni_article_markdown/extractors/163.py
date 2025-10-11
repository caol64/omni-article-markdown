from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import is_matched_canonical


class Netease163Extractor(Extractor):
    """
    163.com
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return is_matched_canonical("https://www.163.com", soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "post_body"})
