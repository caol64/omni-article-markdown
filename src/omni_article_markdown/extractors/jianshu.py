from typing import override

from bs4.element import Tag

from ..extractor import Extractor
from ..utils import filter_tag, get_attr_text, get_og_site_name


class JianshuExtractor(Extractor):
    """
    www.jianshu.com
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "简书"

    @override
    def extract_description(self) -> str:
        return ""

    @override
    def extract_url(self) -> str:
        return "https:"

    @override
    def extract_img(self, element: Tag) -> Tag:
        img_els = element.find_all("img")
        for img_el in img_els:
            img_tag = filter_tag(img_el)
            if img_tag:
                src = get_attr_text(img_tag.attrs.get("data-original-src"))
                if src:
                    img_tag.attrs["src"] = src
        return element
