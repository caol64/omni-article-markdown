from typing import override

from ..extractor import Extractor
from ..utils import is_matched_canonical


class ApiiroBlogExtractor(Extractor):
    """
    Apiiro Blog (apiiro.com/blog/…)

    结构要点：
    - 首屏是 Cloudflare 人机验证页，正文需浏览器渲染后才能拿到，
      故 BrowserReader 以 article.text-gray-700 作为就绪判据
    - 正文在唯一 article.text-gray-700 内；右侧「目录」是容器外的 aside，
      作者/分享/相关文章同样在容器外
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://apiiro.com/blog/", self.soup) and bool(
            self.soup.find("article", class_="text-gray-700")
        )

    @override
    def article_container(self) -> tuple:
        return ("article", {"class": "text-gray-700"})

    @override
    def extract_title(self) -> str:
        # <title> 即文章标题（无站点后缀）；兜底去掉可能的 " | Apiiro" 形式
        title = super().extract_title()
        for suffix in (" | Apiiro", " - Apiiro"):
            if title.endswith(suffix):
                return title.removesuffix(suffix).strip()
        return title
