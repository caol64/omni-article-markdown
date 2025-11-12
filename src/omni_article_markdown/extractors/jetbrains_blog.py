from typing import override

from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import get_og_site_name


class JetbrainsBlogExtractor(Extractor):
    """
    blog.jetbrains.com
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend(
            [
                lambda el: "class" in el.attrs and "content__row" in el.attrs["class"],
                lambda el: "class" in el.attrs and "content__pagination" in el.attrs["class"],
                lambda el: "class" in el.attrs and "content__form" in el.attrs["class"],
                lambda el: "class" in el.attrs and "tag" in el.attrs["class"],
                lambda el: "class" in el.attrs and "author-post" in el.attrs["class"],
            ]
        )

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_site_name(soup) == "The JetBrains Blog"

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "content"})
