from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_title, is_matched_canonical


class SimonWillisonExtractor(Extractor):
    """Simon Willison's Weblog (simonwillison.net)"""

    @override
    def can_handle(self) -> bool:
        # 只接管文章页：首页/存档页只有 div.entry.segment，继续交给 DefaultExtractor
        return is_matched_canonical("https://simonwillison.net", self.soup) and bool(
            self.soup.find("div", class_="entryPage")
        )

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "entryPage"})

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "class" in el.attrs and "entryFooter" in el.attrs["class"],
            lambda el: "class" in el.attrs and "mobile-date" in el.attrs["class"],
            lambda el: "class" in el.attrs and "edit-page-link" in el.attrs["class"],
        ]

    @override
    def extract_description(self) -> str:
        # og:description 只是正文首段的截断，保留会与正文重复
        return ""

    @override
    def pre_handle_soup(self):
        entry = self.soup.find("div", class_="entryPage")
        if not entry:
            return
        # 文章标题写成了 <h2>，归一化为 <h1> 后由基类 remove_duplicate_titles() 去重
        og_title = get_og_title(self.soup).lower()
        first_h2 = entry.find("h2")
        if first_h2 and og_title and first_h2.get_text(strip=True).lower() == og_title:
            first_h2.name = "h1"
        # 站内小节标题用 <h4>，还原语义层级以获得正确的 Markdown 大纲
        for heading in entry.find_all(["h3", "h4"]):
            heading.name = "h2"
        for heading in entry.find_all("h5"):
            heading.name = "h3"
