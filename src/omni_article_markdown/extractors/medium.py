from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_site_name


class MediumExtractor(Extractor):
    """
    Medium
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "Medium"

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "data-testid" in el.attrs,
            lambda el: "class" in el.attrs and "speechify-ignore" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("article", None)
