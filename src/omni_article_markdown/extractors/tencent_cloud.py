from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor


class TencentCloudExtractor(Extractor):
    """
    腾讯云开发者社区
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        title_tag = soup.title
        title = title_tag.get_text(strip=True) if title_tag else None
        return title is not None and title.endswith("-腾讯云开发者社区-腾讯云")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "mod-content__markdown"})
