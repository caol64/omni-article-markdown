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
        if not cards:
            return
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

    @override
    def extract_title(self) -> str:
        title_tag = filter_tag(self.soup.find("div", attrs={"data-testid": "twitter-article-title"}))
        if title_tag:
            title = title_tag.get_text(strip=True)
            title_tag.decompose()  # 从 DOM 中移除标题，避免重复
            return title
        return super().extract_title()
