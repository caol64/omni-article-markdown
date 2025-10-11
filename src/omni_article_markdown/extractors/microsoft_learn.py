from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import get_og_url


class MicrosoftLearnExtractor(Extractor):
    """
    微软技术文档
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend(
            [
                lambda el: "id" in el.attrs and "article-header" in el.attrs["id"],
                lambda el: "id" in el.attrs and "article-metadata" in el.attrs["id"],
                lambda el: "id" in el.attrs and "site-user-feedback-footer" in el.attrs["id"],
            ]
        )

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_url(soup).startswith("https://learn.microsoft.com")

    @override
    def article_container(self) -> tuple:
        return ("main", {"id": "main"})
