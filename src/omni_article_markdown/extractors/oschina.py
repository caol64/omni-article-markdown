from typing import override

from bs4 import BeautifulSoup

from ..extractor import Extractor


class OsChinaExtractor(Extractor):
    """
    开源中国
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        title_tag = soup.title
        title = title_tag.get_text(strip=True) if title_tag else None
        return title is not None and title.endswith(" - OSCHINA - 中文开源技术交流社区")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "detail-box"})
