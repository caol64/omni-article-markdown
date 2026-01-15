from typing import override

from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import get_og_url


class SpringBlogExtractor(Extractor):
    """
    spring.io/blog
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_url(soup).startswith("https://spring.io/blog/")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "markdown"})
