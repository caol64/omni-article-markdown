from typing import override

from ..extractor import Extractor
from ..utils import get_og_url


class SpringBlogExtractor(Extractor):
    """
    spring.io/blog
    """

    @override
    def can_handle(self) -> bool:
        return get_og_url(self.soup).startswith("https://spring.io/blog/")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "markdown"})
