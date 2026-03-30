from abc import ABC, abstractmethod
from pathlib import Path
from typing import override

import requests

from .plugins import load_plugins

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
}


class Reader(ABC):
    def __init__(self, url_or_path: str):
        self.url_or_path = url_or_path

    @abstractmethod
    def read(self) -> str: ...

    @abstractmethod
    def can_handle(self) -> bool: ...


class ReaderFactory:
    @staticmethod
    def create(url_or_path: str) -> Reader:
        if url_or_path.startswith("http"):
            for reader in _load_readers(url_or_path):
                if reader.can_handle():
                    return reader
            return HtmlReader(url_or_path)
        file_reader = FileReader(url_or_path)
        if file_reader.can_handle():
            return file_reader
        raise ValueError(f"No suitable reader found for: {url_or_path}")


class HtmlReader(Reader):
    @override
    def read(self) -> str:
        response = requests.get(self.url_or_path, headers=REQUEST_HEADERS)
        response.encoding = "utf-8"
        return response.text

    @override
    def can_handle(self) -> bool:
        return self.url_or_path.startswith("http")


class FileReader(Reader):
    @override
    def read(self) -> str:
        with open(self.url_or_path, encoding="utf8") as f:
            return f.read()

    @override
    def can_handle(self) -> bool:
        return self.url_or_path.startswith("file://") or Path(self.url_or_path).is_file()


def _load_readers(url_or_path: str) -> list[Reader]:
    return load_plugins(Reader, "readers", url_or_path)
