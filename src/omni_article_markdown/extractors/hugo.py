from typing import override

from ..extractor import Extractor


class HugoExtractor(Extractor):
    """
    Hugo博客
    """

    @override
    def can_handle(self) -> bool:
        return False

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "post-content"})
