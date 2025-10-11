from typing import override
from bs4 import BeautifulSoup
from bs4.element import Tag

from ..extractor import Extractor
from ..utils import filter_tag, get_attr_text, get_og_site_name


class WechatGZHExtractor(Extractor):
    """
    微信公众号
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.append(lambda el: 'id' in el.attrs and el.attrs['id'] == 'meta_content')

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_site_name(soup) == "微信公众平台"

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "rich_media_content"})

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
