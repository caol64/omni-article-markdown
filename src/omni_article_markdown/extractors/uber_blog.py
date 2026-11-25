from typing import override

from ..extractor import Extractor
from ..utils import filter_tag, is_matched_canonical


class UberBlogExtractor(Extractor):
    """
    Uber Blog (www.uber.com/blog/…)

    结构要点：
    - 正文在 div.rich-lfc-content（全页唯一），作者/日期/相关文章都在容器外
    - 正文里的 <h1> 是章节名（Introduction / Conclusion），不是文章标题，
      需降级为 h2，否则 Markdown 会出现多个一级标题、破坏大纲
    - 文章标题取自 <title>，去掉 " | Uber Blog" 之类的后缀
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://www.uber.com/", self.soup) and bool(
            self.soup.find("div", class_="rich-lfc-content")
        )

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "rich-lfc-content"})

    @override
    def extract_title(self) -> str:
        title = super().extract_title()
        for suffix in (" | Uber Blog", " - Uber Blog", " | Uber"):
            if title.endswith(suffix):
                return title.removesuffix(suffix).strip()
        return title

    @staticmethod
    def _split_media_from_headings(body):
        for heading in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            media = [child for child in heading.find_all(recursive=False) if child.find("img") or child.name == "img"]
            if not media:
                continue
            # 把媒体块挪到标题之前，标题只保留文字
            for block in media:
                heading.insert_before(block.extract())
            if not heading.get_text(strip=True):
                heading.decompose()

    @override
    def pre_handle_soup(self):
        body = filter_tag(self.soup.find("div", class_="rich-lfc-content"))
        if not body:
            return
        # 正文 h1 是章节标题，降一级；h2 已是文章内的二级标题，保持不变
        for heading in body.find_all("h1"):
            heading.name = "h2"

        # 源站把图片块塞进了 <h2>（图片 + 图注 + 真正的标题文字混在一起）。
        # 需把图片部分拆到标题之前，只让纯文字留在标题里，
        # 否则 alt 文本和表格等会整体变成 Markdown 标题内容。
        self._split_media_from_headings(body)
