import json
import re
from typing import override

import requests
from bs4 import BeautifulSoup

from ..extractor import Article, Extractor
from ..utils import REQUEST_HEADERS, filter_tag, get_og_url


class YuqueExtractor(Extractor):
    """
    语雀
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return get_og_url(soup).startswith("https://www.yuque.com")

    @override
    def article_container(self) -> tuple:
        return ("", {})

    @override
    def extract_article(self, soup: BeautifulSoup) -> Article:
        script_tag = filter_tag(soup.find("script", string=re.compile(r"decodeURIComponent")))
        if script_tag:
            raw_js = script_tag.string
            if raw_js:
                match = re.search(r'decodeURIComponent\s*\(\s*"([^"]+)"\s*\)', raw_js)
                if match:
                    encoded_str = match.group(1)

                    from urllib.parse import unquote

                    decoded_str = unquote(encoded_str)
                    decoded_json = json.loads(decoded_str)
                    # print(decoded_json)
                    doc = decoded_json["doc"]
                    if doc and doc["book_id"]:
                        book_id = str(doc["book_id"])
                        slug = str(doc["slug"])
                        response = requests.get(f"https://www.yuque.com/api/docs/{slug}?book_id={book_id}&mode=markdown", headers=REQUEST_HEADERS)
                        response.encoding = "utf-8"
                        resp = response.json()
                        # print(resp)
                        return Article(str(resp["data"]["title"]), None, None, str(resp["data"]["sourcecode"]))
        return Article("", None, None, "")
