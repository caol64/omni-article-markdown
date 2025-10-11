from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import is_matched_canonical

class AliyunDeveloperExtractor(Extractor):
    """
    developer.aliyun.com
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return is_matched_canonical("https://developer.aliyun.com", soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article-content"})
