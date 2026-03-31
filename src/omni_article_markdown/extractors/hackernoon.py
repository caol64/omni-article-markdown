import json
from typing import override

from bs4 import BeautifulSoup

from ..extractor import Article, Extractor
from ..utils import filter_tag, get_og_title, is_matched_canonical


class HackernoonExtractor(Extractor):
    """
    hackernoon.com
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://hackernoon.com", self.soup) or get_og_title(self.soup).endswith(" | HackerNoon")

    @override
    def article_container(self) -> tuple:
        return ("article", None)

    @override
    def extract_article(self) -> Article | None:
        tag = filter_tag(self.soup.find("script", {"id": "__NEXT_DATA__"}))
        if tag and tag.string:
            data = json.loads(tag.string)
            data = data.get("props", {}).get("pageProps", {}).get("data", {})
            # print("Parsed JSON:", data)
            image = data.get("mainImage", "")
            body = data.get("parsed", "")
            if image:
                body = f'<img src="{image}" />\n{body}'
            return Article(data.get("title", ""), None, data.get("tldr", ""), BeautifulSoup(body, "html5lib"))

        return None
