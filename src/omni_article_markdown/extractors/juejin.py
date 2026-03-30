from typing import override

from ..extractor import Extractor
from ..utils import filter_tag, is_matched_canonical


class JuejinExtractor(Extractor):
    """
    juejin.cn
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://juejin.cn/", self.soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"id": "article-root"})

    @override
    def extract_title(self) -> str:
        title_tag = filter_tag(self.soup.find("h1", {"class": "article-title"}))
        return title_tag.get_text(strip=True) if title_tag else super().extract_title()
