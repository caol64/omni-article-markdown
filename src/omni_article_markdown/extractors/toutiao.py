from typing import override
from bs4 import BeautifulSoup
from bs4.element import Tag

from ..extractor import Extractor
from ..utils import filter_tag, get_attr_text

class ToutiaoExtractor(Extractor):
    """
    今日头条
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        title_tag = soup.title
        title = title_tag.get_text(strip=True) if title_tag else None
        return title is not None and title.endswith(" - 今日头条")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article-content"})

    @override
    def extract_img(self, element: Tag) -> Tag:
        img_els = element.find_all("img")
        for img_el in img_els:
            img_tag = filter_tag(img_el)
            if img_tag:
                src = get_attr_text(img_tag.attrs.get("data-src"))
                if src:
                    img_tag.attrs["src"] = src
        return element
