from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import get_title


class ClaudeDocExtractor(Extractor):
    """
    Anthropic
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_title(soup).endswith(" \\ Anthropic")

    @override
    def article_container(self) -> tuple:
        return ("article", None)

    @override
    def extract_url(self, soup: BeautifulSoup) -> str:
        return "https://www.anthropic.com/"
