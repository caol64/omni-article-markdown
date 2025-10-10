from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor, get_og_site_name


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
