from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor, get_og_site_name


class MediumExtractor(Extractor):
    """
    Medium
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend([
            lambda el: 'data-testid' in el.attrs,
            lambda el: 'class' in el.attrs and 'speechify-ignore' in el.attrs['class'],
        ])

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_site_name(soup) == "Medium"

    @override
    def article_container(self) -> tuple:
        return ("article", None)
