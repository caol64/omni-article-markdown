from typing import override
from bs4 import BeautifulSoup
from bs4.element import Tag

from ..extractor import ARTICLE_CONTAINERS, Extractor
from ..utils import filter_tag, get_attr_text, get_og_site_name


class JianshuExtractor(Extractor):
    """
    www.jianshu.com
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_site_name(soup) == "简书"

    @override
    def article_container(self) -> tuple | list:
        return ARTICLE_CONTAINERS

    @override
    def extract_description(self, soup: BeautifulSoup) -> str:
        return ""

    @override
    def extract_url(self, soup: BeautifulSoup) -> str:
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
