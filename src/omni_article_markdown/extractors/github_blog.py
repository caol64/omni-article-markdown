from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_title, is_matched_canonical


class GithubBlogExtractor(Extractor):
    """
    The GitHub Blog (github.blog)

    注意：正文区 section.post__content 里**嵌了一段完整的 HTML 文档**
    （`<!DOCTYPE html><html><body>` … `</body></html>`，WordPress 脏数据）。
    html5lib 会在解析时把它拍平，正文成为 post__content 的直接子节点，
    因此容器选择器仍可用；换用 html.parser 则会冒出嵌套的 <html> 节点。
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://github.blog/", self.soup) or get_og_title(self.soup).endswith(
            " - The GitHub Blog"
        )

    @override
    def article_container(self) -> tuple:
        return ("section", {"class": "post__content"})

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            # 文末「Tags: …」标签区
            lambda el: "class" in el.attrs and "my-6" in el.attrs["class"],
            # 文末「Written by …」作者卡片
            lambda el: "class" in el.attrs and "mt-8" in el.attrs["class"] and "mb-8" in el.attrs["class"],
        ]
