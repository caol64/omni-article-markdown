from typing import override

from ..extractor import Extractor
from ..utils import get_title


class AnthropicExtractor(Extractor):
    """
    Anthropic (www.anthropic.com)
    """

    @override
    def can_handle(self) -> bool:
        return get_title(self.soup).endswith(" \\ Anthropic")

    @override
    def article_container(self) -> tuple:
        return ("article", None)

    @override
    def extract_url(self) -> str:
        return "https://www.anthropic.com/"
