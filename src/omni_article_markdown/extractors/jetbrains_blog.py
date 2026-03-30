from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_site_name


class JetbrainsBlogExtractor(Extractor):
    """
    blog.jetbrains.com
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "The JetBrains Blog"

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "content__row" in el.attrs["class"],
            lambda el: "class" in el.attrs and "content__pagination" in el.attrs["class"],
            lambda el: "class" in el.attrs and "content__form" in el.attrs["class"],
            lambda el: "class" in el.attrs and "tag" in el.attrs["class"],
            lambda el: "class" in el.attrs and "author-post" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "content"})
