from bs4 import BeautifulSoup
from ..extractor import Extractor


class WechatGZHExtractor(Extractor):
    """
    微信公众号
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.append(lambda el: 'id' in el.attrs and el.attrs['id'] == 'meta_content')

    def can_handle(self, soup: BeautifulSoup) -> bool:
        return self.get_og_site_name(soup) == "微信公众平台"

    def article_container(self) -> tuple:
        return ("div", {"class": "rich_media_content"})
