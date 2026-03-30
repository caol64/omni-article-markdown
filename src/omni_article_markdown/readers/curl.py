from typing import override

import requests

from ..reader import Reader

TARGET_HOSTS = [
    "https://wallstreetcn.com/articles/",
]


class CurlReader(Reader):
    @override
    def read(self) -> str:
        headers = {"User-Agent": "curl/8.7.1"}
        response = requests.get(self.url_or_path, headers=headers)
        response.encoding = "utf-8"
        return response.text

    @override
    def can_handle(self) -> bool:
        return any(self.url_or_path.startswith(host) for host in TARGET_HOSTS)
