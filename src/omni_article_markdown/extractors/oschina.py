from typing import override

from ..extractor import Extractor
from ..utils import filter_tag, get_title


class OsChinaExtractor(Extractor):
    """
    开源中国 (oschina.net)
    """

    @override
    def can_handle(self) -> bool:
        title = get_title(self.soup)
        return "OSCHINA" in title and ("开源 × AI · 开发者生态社区" in title or "中文开源技术交流社区" in title)

    @override
    def article_container(self) -> list[tuple]:
        # 新版 SPA 正文在 div.editor.heti；detail-box 为旧版模板，保留兼容
        return [("div", {"class": "editor"}), ("div", {"class": "detail-box"})]

    @override
    def extract_title(self) -> str:
        # 新版 og:title 带整串站名后缀，优先取正文区的 h1.blog-content-title
        h1 = filter_tag(self.soup.find("h1", class_="blog-content-title"))
        if h1:
            text = h1.get_text(strip=True)
            if text:
                return text
        return super().extract_title()
