from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import filter_tag


class FreediumExtractor(Extractor):
    """
    freedium.cfd
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        title_tag = soup.title
        title = title_tag.get_text(strip=True) if title_tag else None
        return title is not None and title.endswith(" - Freedium")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "main-content"})

    @override
    def extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = filter_tag(soup.find("h1"))
        if title_tag:
            title = title_tag.get_text(strip=True)
            title_tag.decompose()
            return title
        return super().extract_title(soup)

    @override
    def extract_description(self, soup: BeautifulSoup) -> str:
        description_tag = soup.find("h2")
        if description_tag:
            description = description_tag.get_text(strip=True)
            description_tag.decompose()
            return description
        return super().extract_description(soup)
