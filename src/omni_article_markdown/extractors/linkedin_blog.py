from typing import override

from bs4.element import Tag

from ..extractor import Extractor, TagPredicate
from ..utils import filter_tag, get_attr_text, get_og_url


class LinkedInBlogExtractor(Extractor):
    """
    www.linkedin.com
    """

    @override
    def can_handle(self) -> bool:
        return get_og_url(self.soup).startswith("https://www.linkedin.com/blog/")

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "data-component-type" in el.attrs and "articleHeadline" in el.attrs["data-component-type"],
            lambda el: "data-component-type" in el.attrs and "postList" in el.attrs["data-component-type"],
        ]

    @override
    def extract_img(self, element: Tag) -> Tag:
        img_els = element.find_all("img")
        for img_el in img_els:
            img_tag = filter_tag(img_el)
            if img_tag:
                src = get_attr_text(img_tag.attrs.get("data-delayed-url"))
                if src:
                    img_tag.attrs["src"] = src
        return element
