from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_site_name


class QuantamagazineExtractor(Extractor):
    """
    quantamagazine.org
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "Quanta Magazine"

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "post__title__title" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("div", {"id": "postBody"})
