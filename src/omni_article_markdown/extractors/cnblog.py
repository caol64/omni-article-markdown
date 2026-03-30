from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import is_matched_canonical


class CnBlogsExtractor(Extractor):
    """
    博客园
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://www.cnblogs.com", self.soup)

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "id" in el.attrs and "blog_post_info_block" in el.attrs["id"],
            lambda el: "class" in el.attrs and "postDesc" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "post"})

    @override
    def extract_description(self) -> str:
        return ""
