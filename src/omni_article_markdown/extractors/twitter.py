from typing import override

from bs4 import BeautifulSoup
from bs4.element import Tag

from ..extractor import Extractor
from ..utils import get_og_site_name, get_og_title


class TwitterExtractor(Extractor):
    """
    Twitter/X 推文提取器

    Twitter/X 使用 JavaScript 渲染，需要通过 playwright 来获取完整内容。
    已在 BROWSER_TARGET_HOSTS 中添加了 x.com 和 twitter.com。
    """

    def __init__(self):
        super().__init__()
        # 清理不需要的元素
        self.tags_to_clean.extend(
            [
                lambda el: el.name == "button",
                lambda el: el.name == "svg",
                lambda el: el.name == "path",
            ]
        )
        self.attrs_to_clean.extend(
            [
                lambda el: (
                    "data-testid" in el.attrs
                    and el.attrs.get("data-testid")
                    in [
                        "likeButton",
                        "replyButton",
                        "repostButton",
                        "shareButton",
                        "bookmarkButton",
                        "analyticsButton",
                        "shareButtonMore",
                    ]
                ),
                lambda el: (
                    "aria-label" in el.attrs
                    and any(
                        x in el.attrs["aria-label"]
                        for x in ["Reply", "Repost", "Like", "Share", "Bookmark", "Analytics"]
                    )
                ),
            ]
        )

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        site_name = get_og_site_name(soup)
        return site_name == "X (formerly Twitter)" or "twitter.com" in str(soup) or "x.com" in str(soup)

    @override
    def article_container(self) -> tuple:
        # Twitter 使用 article 标签或 data-testid="tweet" 来标识推文
        return ("article", None)

    @override
    def pre_handle_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        预处理 HTML，提取推文正文内容。

        Twitter 的推文内容结构：
        - 推文容器：<article data-testid="tweet"> 或 <article>
        - 推文文本：在 article 内，通常是在带有特定 class 的 div 中
        - 长文（Thread/Article）：在 public-DraftEditor-content 或 longform-unstyled 类中
        """
        # 查找所有 article 标签
        articles = soup.find_all("article")

        if not articles:
            return soup

        # 创建一个新的容器来存放所有推文内容
        new_content = soup.new_tag("div")
        new_content["class"] = "twitter-thread"

        for article in articles:
            if not isinstance(article, Tag):
                continue
            # 提取推文文本内容
            tweet_text = self._extract_tweet_text(article)
            if tweet_text:
                # 创建一个 p 标签来存放推文文本
                p_tag = soup.new_tag("p")
                p_tag.string = tweet_text
                new_content.append(p_tag)

        # 如果有提取到内容，将其添加到 body
        if len(new_content) > 0:
            body = soup.find("body")
            if body and isinstance(body, Tag):
                # 清空 body 内容，只保留我们提取的内容
                for tag in body.find_all(True):
                    tag.decompose()
                body.append(new_content)

        return soup

    def _extract_tweet_text(self, article: Tag) -> str:
        """
        从 article 标签中提取推文文本。

        Twitter 的推文文本可能在：
        1. public-DraftEditor-content 类中（长文）
        2. longform-unstyled 类中（长文段落）
        3. lang 属性的 div 中（普通推文）
        4. 其他 div 中
        """
        # 首先尝试查找长文内容（DraftEditor）
        draft_editor = article.find("div", class_="public-DraftEditor-content")
        if draft_editor and isinstance(draft_editor, Tag):
            text = draft_editor.get_text(strip=True)
            if text and len(text) > 100:
                return text

        # 尝试查找长文段落（longform-unstyled）
        longform_paragraphs = article.find_all("div", class_="longform-unstyled")
        if longform_paragraphs:
            texts = []
            for p in longform_paragraphs:
                if isinstance(p, Tag):
                    text = p.get_text(strip=True)
                    if text and len(text) > 10:
                        texts.append(text)
            if texts:
                return "\n\n".join(texts)

        # 尝试查找 lang 属性的 div（普通推文）
        text_divs = article.find_all("div", attrs={"lang": True})
        if text_divs:
            texts = []
            for div in text_divs:
                if isinstance(div, Tag):
                    text = div.get_text(strip=True)
                    if text and len(text) > 10:
                        texts.append(text)
            if texts:
                return " ".join(texts)

        # 最后尝试查找包含较长文本的 div
        # 查找所有 div，过滤出包含文本的
        all_divs = article.find_all("div")
        longest_text = ""
        for div in all_divs:
            if not isinstance(div, Tag):
                continue
            # 跳过包含按钮、svg 等的 div
            if div.find(["button", "svg"]):
                continue

            text = div.get_text(strip=True)
            if text and len(text) > len(longest_text) and len(text) > 50:
                longest_text = text

        if longest_text:
            return longest_text

        return ""

    @override
    def extract_title(self, soup: BeautifulSoup) -> str:
        # 使用 og:title 或页面标题
        title = get_og_title(soup)
        if title:
            return title

        # 如果没有 og:title，尝试从推文中提取
        articles = soup.find_all("article")
        if articles:
            first_article = articles[0]
            if isinstance(first_article, Tag):
                first_tweet = self._extract_tweet_text(first_article)
                if first_tweet:
                    # 取推文的前 50 个字符作为标题
                    return first_tweet[:50] + "..." if len(first_tweet) > 50 else first_tweet

        return "Twitter Thread"
