from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import get_og_site_name

class SspaiExtractor(Extractor):
    """
    少数派
    """
    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend(
            [
                lambda el: "class" in el.attrs and "comment__list" in el.attrs["class"],
                lambda el: "class" in el.attrs and "comment__footer__wrapper" in el.attrs["class"],
            ]
        )

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_site_name(soup) == "少数派 - 高品质数字消费指南"

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article__main__wrapper"})
