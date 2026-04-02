from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import filter_tag, get_attr_text, get_title


class FeishuExtractor(Extractor):
    """
    飞书云文档
    """

    @override
    def can_handle(self) -> bool:
        return get_title(self.soup).endswith(" - 飞书云文档")

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "data-type" in el.attrs and "print-forbidden-placeholder" in el.attrs["data-type"],
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
        """
        https://open.feishu.cn/document/docs/docs/data-structure/block
        """

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
        attr_map = {
            ".inline-code": "code",
            ".code-block-zone-container": "code",
        }
        for el in self.soup.select("div[data-block-type]"):
            tag = filter_tag(el)
            if not tag:
                continue
            block_type = get_attr_text(el.get("data-block-type"))
            tag.name = tag_map.get(block_type if block_type else "", "p")
            tag.attrs = {}

        for attr_selector, new_tag in attr_map.items():
            for el in self.soup.select(attr_selector):
                tag = filter_tag(el)
                if not tag:
                    continue
                tag.name = new_tag
                tag.attrs = {}
