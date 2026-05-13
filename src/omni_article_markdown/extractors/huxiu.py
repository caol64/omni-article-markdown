from typing import override

from ..extractor import Extractor
from ..utils import get_og_site_name


class HuxiuExtractor(Extractor):
    """虎嗅网"""

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "虎嗅网"

    @override
    def extract_title(self) -> str:
        h1 = self.soup.find("h1", class_="article__title")
        if h1:
            return h1.get_text(strip=True)
        return super().extract_title()

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "article__content"})
