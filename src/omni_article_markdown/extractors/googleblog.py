from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_title


class GoogleBlogExtractor(Extractor):
    """
    developers.googleblog.com
    """

    @override
    def can_handle(self) -> bool:
        return get_og_title(self.soup).endswith("- Google Developers Blog")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "blog-detail-container"})

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "tags-container" in el.attrs["class"],
            lambda el: "class" in el.attrs and "summary-container" in el.attrs["class"],
            lambda el: "class" in el.attrs and "author-container" in el.attrs["class"],
            lambda el: "class" in el.attrs and "social-container" in el.attrs["class"],
            lambda el: "class" in el.attrs and "navigation-container" in el.attrs["class"],
            lambda el: "class" in el.attrs and "related-posts-container" in el.attrs["class"],
        ]
