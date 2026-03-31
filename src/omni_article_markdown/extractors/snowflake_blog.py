from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import is_matched_canonical


class SnowflakeBlogExtractor(Extractor):
    """
    Snowflake 技术博客
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://www.snowflake.com/en/blog/", self.soup)

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "snowflake-header-container" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "snowflake-responsive-container-inner-padding-medium"})
