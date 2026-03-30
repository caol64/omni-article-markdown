from typing import override

from bs4.element import Tag

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_site_name, get_og_title, get_tag_text


class TwitterExtractor(Extractor):
    """
    Twitter/X 推文提取器

    Twitter/X 使用 JavaScript 渲染，需要通过 playwright 来获取完整内容。
    """

    @override
    def can_handle(self) -> bool:
        return get_og_site_name(self.soup) == "X (formerly Twitter)"

    # @override
    # def get_tags_to_clean(self) -> list[TagPredicate]:
    #     return super().get_tags_to_clean() + [
    #         lambda el: el.name == "button",
    #         lambda el: el.name == "svg",
    #         lambda el: el.name == "path",
    #     ]

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            lambda el: (
                "data-testid" in el.attrs
                and el.attrs.get("data-testid")
                in [
                    "simpleTweet",
                ]
            ),
            lambda el: (
                "aria-live" in el.attrs
                and el.attrs.get("aria-live")
                in [
                    "polite",
                ]
            ),
        ]

    @override
    def article_container(self) -> tuple:
        # Twitter 使用 article 标签或 data-testid="tweet" 来标识推文
        return ("article", None)

    # @override
    # def pre_handle_soup(self):
    #     """
    #     预处理 HTML，提取推文正文内容。

    #     Twitter 的推文内容结构：
    #     - 推文容器：<article data-testid="tweet"> 或 <article>
    #     - 推文文本：在 article 内，通常是在带有特定 class 的 div 中
    #     - 长文（Thread/Article）：在 public-DraftEditor-content 或 longform-unstyled 类中
    #     """
    #     # 查找所有 article 标签
    #     articles = self.soup.find_all("article")

    #     if not articles:
    #         return

    #     # 创建一个新的容器来存放所有推文内容
    #     new_content = self.soup.new_tag("div")
    #     new_content["class"] = "twitter-thread"

    #     for article in articles:
    #         if not isinstance(article, Tag):
    #             continue
    #         # 提取推文文本内容
    #         tweet_text = self._extract_tweet_text(article)
    #         if tweet_text:
    #             # 创建一个 p 标签来存放推文文本
    #             p_tag = self.soup.new_tag("p")
    #             p_tag.string = tweet_text
    #             new_content.append(p_tag)

    #     # 如果有提取到内容，将其添加到 body
    #     if len(new_content) > 0:
    #         body = self.soup.find("body")
    #         if body and isinstance(body, Tag):
    #             # 清空 body 内容，只保留我们提取的内容
    #             for tag in body.find_all(True):
    #                 tag.decompose()
    #             body.append(new_content)

    # def _extract_tweet_text(self, article: Tag) -> str:
    #     """
    #     从 article 标签中提取推文文本。

    #     Twitter 的推文文本可能在：
    #     1. public-DraftEditor-content 类中（长文）
    #     2. longform-unstyled 类中（长文段落）
    #     3. lang 属性的 div 中（普通推文）
    #     4. 其他 div 中
    #     """
    #     # 首先尝试查找长文内容（DraftEditor）
    #     draft_editor = article.find("div", class_="public-DraftEditor-content")
    #     if draft_editor and isinstance(draft_editor, Tag):
    #         text = draft_editor.get_text(strip=True)
    #         if text and len(text) > 100:
    #             return text

    #     # 尝试查找长文段落（longform-unstyled）
    #     longform_paragraphs = article.find_all("div", class_="longform-unstyled")
    #     if longform_paragraphs:
    #         texts = []
    #         for p in longform_paragraphs:
    #             if isinstance(p, Tag):
    #                 text = p.get_text(strip=True)
    #                 if text and len(text) > 10:
    #                     texts.append(text)
    #         if texts:
    #             return "\n\n".join(texts)

    #     # 尝试查找 lang 属性的 div（普通推文）
    #     text_divs = article.find_all("div", attrs={"lang": True})
    #     if text_divs:
    #         texts = []
    #         for div in text_divs:
    #             if isinstance(div, Tag):
    #                 text = div.get_text(strip=True)
    #                 if text and len(text) > 10:
    #                     texts.append(text)
    #         if texts:
    #             return " ".join(texts)

    #     # 最后尝试查找包含较长文本的 div
    #     # 查找所有 div，过滤出包含文本的
    #     all_divs = article.find_all("div")
    #     longest_text = ""
    #     for div in all_divs:
    #         if not isinstance(div, Tag):
    #             continue
    #         # 跳过包含按钮、svg 等的 div
    #         if div.find(["button", "svg"]):
    #             continue

    #         text = div.get_text(strip=True)
    #         if text and len(text) > len(longest_text) and len(text) > 50:
    #             longest_text = text

    #     if longest_text:
    #         return longest_text

    #     return ""

    @override
    def extract_title(self) -> str:
        title_tag = self.soup.find("div", attrs={"data-testid": "twitter-article-title"})
        title = title_tag.get_text(strip=True) if title_tag else ""
        return title if title else get_og_title(self.soup)
