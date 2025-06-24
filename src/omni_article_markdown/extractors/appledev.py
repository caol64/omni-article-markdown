from bs4 import BeautifulSoup
from ..extractor import Extractor


class AppleDevelopExtractor(Extractor):
    """
    Apple Developer Documentation
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend([
            lambda el: 'class' in el.attrs and 'eyebrow' in el.attrs['class'],
            lambda el: 'class' in el.attrs and 'platform' in el.attrs['class'],
            lambda el: 'class' in el.attrs and 'title' in el.attrs['class'],
        ])

    def can_handle(self, soup: BeautifulSoup) -> bool:
        return self.get_og_site_name(soup) == "Apple Developer Documentation"

    def article_container(self) -> tuple:
        return ("main", {"class": "main"})
