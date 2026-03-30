from typing import override

from ..extractor import Extractor
from ..utils import get_og_site_name


class AndroidDevelopersBlogExtractor(Extractor):
    """
    Android Developers Blog
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "Android Developers Blog"

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "adb-detail__content"})
