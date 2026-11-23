from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_title


class ClaudeDocExtractor(Extractor):
    """
    docs.claude.com
    """

    @override
    def can_handle(self) -> bool:
        return get_og_title(self.soup).endswith(" - Claude Docs")

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "data-component-part" in el.attrs and "code-block-header" in el.attrs["data-component-part"],
            lambda el: "data-component-part" in el.attrs and "code-group-tab-bar" in el.attrs["data-component-part"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "mdx-content"})
