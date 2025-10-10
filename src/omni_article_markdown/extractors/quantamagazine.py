from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor, get_og_site_name


class QuantamagazineExtractor(Extractor):
    """
    quantamagazine.org
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend([
            lambda el: 'class' in el.attrs and 'post__title__title' in el.attrs['class'],
        ])

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_site_name(soup) == "Quanta Magazine"

    @override
    def article_container(self) -> tuple:
        return ("div", {"id": "postBody"})
