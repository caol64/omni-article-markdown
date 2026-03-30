from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_site_name


class TowardsDataScienceExtractor(Extractor):
    """
    towardsdatascience.com
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "Towards Data Science"

    @override
    def get_tags_to_clean(self) -> list[TagPredicate]:
        return super().get_tags_to_clean() + [
            lambda el: el.name == "time",
        ]

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "taxonomy-post_tag" in el.attrs["class"],
            lambda el: "class" in el.attrs and "tds-cta-box" in el.attrs["class"],
            lambda el: "class" in el.attrs and "wp-block-buttons" in el.attrs["class"],
            lambda el: "class" in el.attrs and "wp-block-outermost-social-sharing" in el.attrs["class"],
            lambda el: "class" in el.attrs and "wp-block-tenup-post-time-to-read" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("main", None)
