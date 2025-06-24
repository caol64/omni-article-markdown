from bs4 import BeautifulSoup
from ..extractor import Extractor


class HugoExtractor(Extractor):
    """
    Hugo博客
    """

    def can_handle(self, soup: BeautifulSoup) -> bool:
        return False

    def article_container(self) -> tuple:
        return ("div", {"class": "post-content"})
