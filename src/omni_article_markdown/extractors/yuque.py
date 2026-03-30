import json
import re
from typing import override

import requests

from ..extractor import Article, Extractor
from ..reader import REQUEST_HEADERS
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
    def extract_article(self) -> Article:
        # script_tag = filter_tag(self.soup.find("script", string=re.compile(r"decodeURIComponent")))
        # if script_tag:
        #     raw_js = script_tag.string
        #     if raw_js:
        #         match = re.search(r'decodeURIComponent\s*\(\s*"([^"]+)"\s*\)', raw_js)
        #         if match:
        #             encoded_str = match.group(1)

        #             from urllib.parse import unquote

        #             decoded_str = unquote(encoded_str)
        #             decoded_json = json.loads(decoded_str)
        #             # print(decoded_json)
        #             doc = decoded_json["doc"]
        #             if doc and doc["book_id"]:
        #                 book_id = str(doc["book_id"])
        #                 slug = str(doc["slug"])
        #                 response = requests.get(
        #                     f"https://www.yuque.com/api/docs/{slug}?book_id={book_id}&mode=markdown",
        #                     headers=REQUEST_HEADERS,
        #                 )
        #                 response.encoding = "utf-8"
        #                 resp = response.json()
        #                 # print(resp)
        #                 return Article(str(resp["data"]["title"]), None, None, str(resp["data"]["sourcecode"]))
        return Article("", None, None, "")
