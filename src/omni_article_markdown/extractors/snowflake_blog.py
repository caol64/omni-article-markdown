from typing import override

from ..extractor import Extractor
from ..utils import get_canonical_url


class SnowflakeBlogExtractor(Extractor):
    """
    Snowflake 技术博客
    """

    @override
    def can_handle(self) -> bool:
        # 通过 canonical URL 和特有的 class 来识别
        canonical = get_canonical_url(self.soup)
        if canonical and "snowflake.com/en/blog" in canonical:
            return True
        # 也可以通过特有的 class 来识别
        return self.soup.find("div", class_="snowflake-blog-text") is not None

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "snowflake-blog-text"})
