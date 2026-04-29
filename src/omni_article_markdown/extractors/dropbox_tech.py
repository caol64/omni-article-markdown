from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import filter_tag, is_matched_canonical


class DropboxTechExtractor(Extractor):
    """
    dropbox.tech
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://dropbox.tech", self.soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "dr-article-content__content"})

    @override
    def get_tags_to_clean(self) -> list[TagPredicate]:
        return super().get_tags_to_clean() + [
            lambda el: el.name == "nav",
        ]

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "id" in el.attrs and "cta" in el.attrs["id"],
        ]

    @override
    def pre_handle_soup(self):
        for tag in self.soup.find_all("span", {"class": "dr-code"}):
            span_tag = filter_tag(tag)
            if span_tag:
                span_tag.name = "code"
