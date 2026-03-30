from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import is_matched_canonical


class InfoQExtractor(Extractor):
    """
    www.infoq.com
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://www.infoq.com", self.soup)

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "author-section-full" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article__data"})
