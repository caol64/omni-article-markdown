import json
import re
from typing import override

from ..extractor import Article, Extractor
from ..http_client import get_session
from ..utils import filter_tag, get_og_url


class YuqueExtractor(Extractor):
    """
    语雀
    """

    @override
    def can_handle(self) -> bool:
        return get_og_url(self.soup).startswith("https://www.yuque.com")

    @override
    def article_container(self) -> tuple:
        return ("", {})

    @override
    def extract_article(self) -> Article | None:
        script_tag = filter_tag(self.soup.find("script", text=re.compile(r"decodeURIComponent")))
        if not script_tag or not script_tag.string:
            return None
        raw_js = script_tag.string.strip()
        match = re.search(r'decodeURIComponent\s*\(\s*"([^"]+)"\s*\)', raw_js)
        if not match:
            return None
        encoded_str = match.group(1)

        from urllib.parse import unquote

        decoded_str = unquote(encoded_str)
        decoded_json = json.loads(decoded_str)
        # print(decoded_json)
        doc = decoded_json.get("doc")
        if doc and doc.get("book_id") and doc.get("slug"):
            book_id = str(doc["book_id"])
            slug = str(doc["slug"])
            response = get_session().get(
                f"https://www.yuque.com/api/docs/{slug}?book_id={book_id}&mode=markdown",
            )
            response.encoding = "utf-8"
            resp = response.json()
            # print(resp)
            return Article(str(resp["data"]["title"]), None, None, str(resp["data"]["sourcecode"]))
        return None
