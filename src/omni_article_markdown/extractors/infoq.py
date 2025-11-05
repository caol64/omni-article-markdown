from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import is_matched_canonical


class InfoQExtractor(Extractor):
    """
    www.infoq.com
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend(
            [
                lambda el: "class" in el.attrs and "author-section-full" in el.attrs["class"],
            ]
        )

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return is_matched_canonical("https://www.infoq.com", soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article__data"})
