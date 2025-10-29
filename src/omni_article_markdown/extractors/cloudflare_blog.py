from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import is_matched_canonical


class CloudflareBlogExtractor(Extractor):
    """
    blog.cloudflare.com
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return is_matched_canonical("https://blog.cloudflare.com", soup)

    @override
    def article_container(self) -> tuple:
        return ("section", {"class": "post-full-content"})
