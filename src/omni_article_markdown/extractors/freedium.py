from typing import override

from ..extractor import Extractor
from ..utils import filter_tag


class FreediumExtractor(Extractor):
    """
    freedium.cfd
    """

    @override
    def can_handle(self) -> bool:
        title_tag = self.soup.title
        title = title_tag.get_text(strip=True) if title_tag else None
        return title is not None and title.endswith(" - Freedium")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "main-content"})

    @override
    def extract_title(self) -> str:
        title_tag = filter_tag(self.soup.find("h1"))
        if title_tag:
            title = title_tag.get_text(strip=True)
            title_tag.decompose()
            return title
        return super().extract_title()

    @override
    def extract_description(self) -> str:
        description_tag = self.soup.find("h2")
        if description_tag:
            description = description_tag.get_text(strip=True)
            description_tag.decompose()
            return description
        return super().extract_description()
