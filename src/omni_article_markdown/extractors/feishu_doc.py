from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import filter_tag, get_title


class FeishuDocExtractor(Extractor):
    """
    飞书云文档
    """

    @override
    def can_handle(self) -> bool:
        return get_title(self.soup).endswith(" - 飞书云文档")

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "author-section-full" in el.attrs["class"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "page-block-children"})

    @override
    def extract_title(self) -> str:
        title = get_title(self.soup)
        return title.replace(" - 飞书云文档", "")

    @override
    def pre_handle_soup(self):
        tag_map = {
            "heading1": "h1",
            "heading2": "h2",
            "heading3": "h3",
            "heading4": "h4",
            "heading5": "h5",
            "heading6": "h6",
            "text": "p",
            "quote_container": "blockquote",
            "code": "pre",
        }
        for block_type, block_tag in tag_map.items():
            for el in self.soup.find_all("div", attrs={"data-block-type": block_type}):
                tag = filter_tag(el)
                if not tag:
                    continue
                tag.name = block_tag
                tag.attrs = {}
