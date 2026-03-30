from typing import override

from ..extractor import Extractor
from ..utils import is_matched_canonical


class AliyunDeveloperExtractor(Extractor):
    """
    developer.aliyun.com
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://developer.aliyun.com", self.soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article-content"})
