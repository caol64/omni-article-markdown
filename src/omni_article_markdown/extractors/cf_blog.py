from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor, is_matched_canonical


class CloudflareBlogxtractor(Extractor):
    """
    blog.cloudflare.com
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return is_matched_canonical("https://blog.cloudflare.com", soup)

    @override
    def article_container(self) -> tuple:
        return ("section", {"class": "post-full-content"})
