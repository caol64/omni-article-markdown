from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import is_matched_canonical

class CnBlogsExtractor(Extractor):
    """
    博客园
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend(
            [
                lambda el: "id" in el.attrs and "blog_post_info_block" in el.attrs["id"],
                lambda el: "class" in el.attrs and "postDesc" in el.attrs["class"],
            ]
        )

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return is_matched_canonical("https://www.cnblogs.com", soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "post"})

    @override
    def extract_description(self, soup: BeautifulSoup) -> str:
        return ""
