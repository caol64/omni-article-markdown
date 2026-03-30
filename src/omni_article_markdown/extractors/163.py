from typing import override

from ..extractor import Extractor
from ..utils import is_matched_canonical


class Netease163Extractor(Extractor):
    """
    163.com
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://www.163.com", self.soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "post_body"})
