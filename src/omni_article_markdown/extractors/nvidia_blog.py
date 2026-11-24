from typing import override

from ..extractor import Extractor
from ..utils import filter_tag, is_matched_canonical


class NvidiaTechnicalBlogExtractor(Extractor):
    """
    NVIDIA Technical Blog (developer.nvidia.com/blog/…)

    正文在 div.entry-content 内；分类行、AI 摘要（details.nv-ai-summary）、
    标签、About the Authors、Comments 都在容器外，收窄容器即可排除。
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://developer.nvidia.com/blog/", self.soup) and bool(
            self.soup.find("div", class_="entry-content")
        )

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "entry-content"})

    @override
    def extract_title(self) -> str:
        # og:title 带 " | NVIDIA Technical Blog" 后缀，优先取页面 h1
        h1 = filter_tag(self.soup.find("h1"))
        if h1:
            text = h1.get_text(strip=True)
            if text:
                return text
        return super().extract_title()

    @override
    def extract_description(self) -> str:
        # og:description 是首段截断，与正文重复
        return ""
