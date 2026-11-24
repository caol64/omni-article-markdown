from typing import override

from ..extractor import Extractor
from ..utils import filter_tag, is_matched_canonical


class YuzhiDocsExtractor(Extractor):
    """
    遇之文档 (yuzhi.tech)

    正文在 div.prose 内；「上一篇 / 下一篇」是正文外的 nav，
    「本页目录」是同级的 aside，收窄容器即可一并排除。
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://yuzhi.tech/", self.soup) and bool(self.soup.find("div", class_="prose"))

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "prose"})

    @override
    def extract_description(self) -> str:
        # og:description 只是正文首段（或其前半句）的重复，生成摘要会与正文重复
        return ""

    @override
    def extract_title(self) -> str:
        # 正文首行的 h1 才是页面标题；og:title 可能是所属栏目名（如「主题系统」而非「自定义主题」）
        prose = filter_tag(self.soup.find("div", class_="prose"))
        if prose:
            h1 = filter_tag(prose.find("h1"))
            if h1:
                text = h1.get_text(strip=True)
                if text:
                    return text
        # 兜底：og:title 形如 "基本功能 | 文颜"，去掉产品后缀
        title = super().extract_title()
        if " | " in title:
            return title.split(" | ", 1)[0].strip()
        return title
