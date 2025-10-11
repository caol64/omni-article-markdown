from typing import override
from bs4 import BeautifulSoup

from ..extractor import ARTICLE_CONTAINERS, Extractor
from ..utils import get_og_site_name


class JianshuExtractor(Extractor):
    """
    www.jianshu.com
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_site_name(soup) == "简书"

    @override
    def article_container(self) -> tuple | list:
        return ARTICLE_CONTAINERS

    @override
    def extract_url(self, soup: BeautifulSoup) -> str:
        return "https:"
