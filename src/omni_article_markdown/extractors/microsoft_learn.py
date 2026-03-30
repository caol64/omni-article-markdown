from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_url


class MicrosoftLearnExtractor(Extractor):
    """
    微软技术文档
    """

    @override
    def can_handle(self) -> bool:
        return get_og_url(self.soup).startswith("https://learn.microsoft.com")

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "id" in el.attrs and "article-header" in el.attrs["id"],
            lambda el: "id" in el.attrs and "article-metadata" in el.attrs["id"],
            lambda el: "id" in el.attrs and "site-user-feedback-footer" in el.attrs["id"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("main", {"id": "main"})
