from typing import override
from urllib.parse import parse_qs, urlparse

from ..extractor import Extractor
from ..utils import filter_tag, get_attr_text, is_matched_canonical


class CloudflareBlogExtractor(Extractor):
    """
    blog.cloudflare.com
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://blog.cloudflare.com", self.soup)

    @override
    def article_container(self) -> list[tuple]:
        # 新模板正文在 div.article-content；section.post-full-content 为旧模板；main 兜底
        return [
            ("div", {"class": "article-content"}),
            ("section", {"class": "post-full-content"}),
            ("main", None),
        ]

    @override
    def pre_handle_soup(self):
        # 图片被 /_image 图片处理代理包了一层，还原成原始图片地址
        body = filter_tag(self.soup.find("div", class_="article-content")) or filter_tag(
            self.soup.find("section", class_="post-full-content")
        )
        if not body:
            return
        for element in body.find_all("img"):
            img = filter_tag(element)
            if not img:
                continue
            original = parse_qs(urlparse(get_attr_text(img.get("src"))).query).get("href")
            if original:
                img["src"] = original[0]
                img.attrs.pop("srcset", None)
