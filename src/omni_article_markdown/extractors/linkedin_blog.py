from typing import override

from bs4 import BeautifulSoup
from bs4.element import Tag

from ..extractor import ARTICLE_CONTAINERS, Extractor
from ..utils import filter_tag, get_attr_text, get_og_url


class LinkedInBlogExtractor(Extractor):
    """
    www.linkedin.com
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend(
            [
                lambda el: "data-component-type" in el.attrs and "articleHeadline" in el.attrs["data-component-type"],
                lambda el: "data-component-type" in el.attrs and "postList" in el.attrs["data-component-type"],
            ]
        )

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_url(soup).startswith("https://www.linkedin.com/blog/")

    @override
    def article_container(self) -> list[tuple]:
        return ARTICLE_CONTAINERS

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
