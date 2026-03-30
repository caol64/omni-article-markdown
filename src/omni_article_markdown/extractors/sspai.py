from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_site_name


class SspaiExtractor(Extractor):
    """
    少数派
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "少数派 - 高品质数字消费指南"

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "comment__list" in el.attrs["class"],
            lambda el: "class" in el.attrs and "comment__footer__wrapper" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article__main__wrapper"})
