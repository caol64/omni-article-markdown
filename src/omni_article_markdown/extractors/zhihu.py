from typing import override

from ..extractor import Extractor
from ..utils import get_og_site_name


class ZhihuExtractor(Extractor):
    """
    知乎专栏
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "知乎专栏"

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "Post-RichText"})
