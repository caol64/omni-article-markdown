from typing import override

from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import get_og_site_name


class AndroidDevelopersBlogExtractor(Extractor):
    """
    Android Developers Blog
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_site_name(soup) == "Android Developers Blog"

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "adb-detail__content"})
