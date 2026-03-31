from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_site_name


class AppleDevelopExtractor(Extractor):
    """
    Apple Developer Documentation
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "Apple Developer Documentation"

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "eyebrow" in el.attrs["class"],
            lambda el: "class" in el.attrs and "platform" in el.attrs["class"],
            lambda el: "class" in el.attrs and "title" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("main", {"class": "main"})
