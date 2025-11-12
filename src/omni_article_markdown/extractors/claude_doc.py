from typing import override

from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import get_og_title


class ClaudeDocExtractor(Extractor):
    """
    docs.claude.com
    """

    def __init__(self):
        super().__init__()
        self.attrs_to_clean.extend(
            [
                lambda el: "data-component-part" in el.attrs and "code-block-header" in el.attrs["data-component-part"],
                lambda el: "data-component-part" in el.attrs and "code-group-tab-bar" in el.attrs["data-component-part"],
            ]
        )

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_title(soup).endswith(" - Claude Docs")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "mdx-content"})
