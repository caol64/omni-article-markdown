from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import filter_tag, get_og_site_name, get_tag_text


class TwitterExtractor(Extractor):
    """
    Twitter/X 推文提取器
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "X (formerly Twitter)"

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: "data-testid" in el.attrs and "simpleTweet" in el.attrs["data-testid"],
            lambda el: "aria-live" in el.attrs and "polite" in el.attrs["aria-live"],
            lambda el: "role" in el.attrs and "group" in el.attrs["role"],
        ]

    @override
    def article_container(self) -> tuple:
        return ("article", {"data-testid": "tweet"})

    @override
    def pre_handle_soup(self):
        # 查找所有卡片
        cards = self.soup.find_all(attrs={"data-testid": "simpleTweet"})
        if cards:
            for card in cards:
                card_tag = filter_tag(card)
                if not card_tag:
                    continue
                links = card_tag.find_all("a", href=True)
                for link in links:
                    href = get_tag_text(link, "href")
                    if href.endswith("/analytics"):
                        target_url = f"https://x.com{href.replace('/analytics', '')}"
                        new_a_tag = self.soup.new_tag("a", href=target_url)
                        new_a_tag.string = "link"
                        card.replace_with(new_a_tag)
                        break

        # 修复段落结构：Twitter/X 使用 data-offset-key 和 longform 样式来分段
        # 查找所有 class 包含 longform 的 div 元素（代表段落）
        # 用 <p> 标签包裹它们，以便后续正确转换为 markdown
        paragraphs = self.soup.select("div[class*='longform']")
        for para in paragraphs:
            span_tag = para.find("span", attrs={"data-text": "true"})
            if span_tag:
                # 获取带换行的原始文本
                raw_text = span_tag.get_text(separator="\n", strip=False)
                if "\n" in raw_text:
                    # 按换行分割成干净段落
                    lines = [
                        line.strip() for line in raw_text.split("\n")
                        if line.strip()
                    ]

                    # 把每一行都变成 <p> 标签
                    for text in lines:
                        new_p = self.soup.new_tag("p")
                        new_p.string = text
                        span_tag.insert_before(new_p)

                    # 删除原来的 span
                    span_tag.decompose()
                    continue

            # 检查是否已经被 <p> 标签包裹
            if para.parent and para.parent.name == "p":
                continue
            # 创建新的 p 标签
            p_tag = self.soup.new_tag("p")
            # 将段落内容移动到 p 标签内
            para.wrap(p_tag)

    @override
    def extract_title(self) -> str:
        title_tag = filter_tag(self.soup.find("div", attrs={"data-testid": "twitter-article-title"}))
        if title_tag:
            title = title_tag.get_text(strip=True)
            title_tag.decompose()  # 从 DOM 中移除标题，避免重复
            return title
        return super().extract_title()
