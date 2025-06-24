from bs4 import BeautifulSoup
from ..extractor import Extractor


class ZhihuExtractor(Extractor):
    """
    知乎专栏
    """

    def can_handle(self, soup: BeautifulSoup) -> bool:
        return self.get_og_site_name(soup) == "知乎专栏"

    def article_container(self) -> tuple:
        return ("div", {"class": "Post-RichText"})
