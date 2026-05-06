from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_canonical_url


class WikipediaExtractor(Extractor):
    """
    wikipedia.org
    """

    @override
    def can_handle(self) -> bool:
        return get_canonical_url(self.soup).index("wikipedia.org/wiki/") != -1

    @override
    def article_container(self) -> tuple:
        return ("div", {"id": "bodyContent"})

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "id" in el.attrs and "siteSub" in el.attrs["id"],
            lambda el: "class" in el.attrs and "vector-body-before-content" in el.attrs["class"],
            lambda el: "class" in el.attrs and "mw-editsection" in el.attrs["class"],
            lambda el: "role" in el.attrs and "navigation" in el.attrs["role"],
            lambda el: "role" in el.attrs and "presentation" in el.attrs["role"],
            lambda el: "class" in el.attrs and "printfooter" in el.attrs["class"],
            lambda el: "class" in el.attrs and "side-box" in el.attrs["class"],
            lambda el: "class" in el.attrs and "reflist" in el.attrs["class"],
            lambda el: "class" in el.attrs and "div-col" in el.attrs["class"],
            lambda el: "class" in el.attrs and "mw-references" in el.attrs["class"],
            lambda el: "class" in el.attrs and "mw-references-wrap" in el.attrs["class"],
            lambda el: "class" in el.attrs and "mw-references-columns" in el.attrs["class"],
            lambda el: "class" in el.attrs and "refbegin" in el.attrs["class"],
            lambda el: "id" in el.attrs and "catlinks" in el.attrs["id"],
            lambda el: el.name == "sup" and ("class" in el.attrs and "reference" in el.attrs["class"]),
        ]

    @override
    def extract_url(self) -> str:
        return get_canonical_url(self.soup)
