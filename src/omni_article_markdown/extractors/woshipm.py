from typing import override

from ..extractor import Extractor
from ..utils import get_og_url


class WoShiPMExtractor(Extractor):
    """
    人人都是产品经理
    """

    @override
    def can_handle(self) -> bool:
        return get_og_url(self.soup).startswith("https://www.woshipm.com")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article--content"})
