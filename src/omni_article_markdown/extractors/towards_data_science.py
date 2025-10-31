from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import get_og_site_name


class TowardsDataScienceExtractor(Extractor):
    """
    towardsdatascience.com
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend([
            lambda el: 'class' in el.attrs and 'taxonomy-post_tag' in el.attrs['class'],
            lambda el: 'class' in el.attrs and 'tds-cta-box' in el.attrs['class'],
            lambda el: 'class' in el.attrs and 'wp-block-buttons' in el.attrs['class'],
            lambda el: 'class' in el.attrs and 'wp-block-outermost-social-sharing' in el.attrs['class'],
            lambda el: 'class' in el.attrs and 'wp-block-tenup-post-time-to-read' in el.attrs['class'],
        ])
        self.tags_to_clean.extend([
            lambda el: el.name == 'time',
        ])

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_site_name(soup) == "Towards Data Science"

    @override
    def article_container(self) -> tuple | list:
        return ("main", None)
