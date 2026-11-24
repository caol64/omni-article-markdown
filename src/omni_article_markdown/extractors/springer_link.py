from typing import override

from ..extractor import Extractor
from ..utils import filter_tag, get_attr_text, is_matched_canonical


class SpringerLinkExtractor(Extractor):
    """
    SpringerLink (link.springer.com)

    结构要点：
    - 章节在 div.c-article-body > div.main-content
    - 但 Data availability / Notes / References / Funding / Appendices 是
      main-content 的**兄弟节点**，所以容器必须取外层 div.c-article-body，
      再靠清理谓词精确剔除模板噪音
    - 摘要单独挂在 c-article-body 下（aria-labelledby="Abs1"）
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://link.springer.com/article/", self.soup)

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "c-article-body"})

    @override
    def extract_title(self) -> str:
        # og:title 带 " - Artificial Intelligence Review" 这类期刊后缀，优先取 h1
        h1 = filter_tag(self.soup.find("h1", class_="c-article-title"))
        if h1:
            return h1.get_text(strip=True)
        return super().extract_title()

    @override
    def extract_description(self) -> str:
        # Abstract 章节本身已在正文里，再生成摘要会与正文重复
        return ""

    @override
    def get_attrs_to_clean(self) -> list:
        return super().get_attrs_to_clean() + [
            # 「Similar content being viewed by others」推荐位
            lambda el: "class" in el.attrs and "c-article-recommendations" in el.attrs["class"],
            # 「Explore related subjects」学科推荐位
            lambda el: "class" in el.attrs and "app-explore-related-subjects" in el.attrs["class"],
            # 「Profiles」作者档案侧栏
            lambda el: el.get("id") == "researcher-profile-container",
            # CrossMark 徽标（内联 base64 SVG）：无文字语义，渲染出来只是一张图
            lambda el: el.name == "img" and "check for updates" in get_attr_text(el.attrs.get("alt")).lower(),
        ]
