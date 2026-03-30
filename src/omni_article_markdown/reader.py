from abc import ABC, abstractmethod
from pathlib import Path
from typing import override

import requests

from .plugins import load_plugins
from .reporter import Reporter

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
}


class Reader(ABC):
    def __init__(self, url_or_path: str, reporter: Reporter | None = None):
        self.url_or_path = url_or_path
        self.reporter = reporter

    @abstractmethod
    def read(self) -> str: ...

    @abstractmethod
    def can_handle(self) -> bool: ...

    def report(self, message: str):
        if self.reporter:
            self.reporter(message)


class ReaderFactory:
    @staticmethod
    def create(url_or_path: str, reporter: Reporter | None = None) -> Reader:
        if url_or_path.startswith("http"):
            for reader in _load_readers(url_or_path, reporter=reporter):
                if reader.can_handle():
                    return reader
            return HtmlReader(url_or_path, reporter=reporter)
        file_reader = FileReader(url_or_path, reporter=reporter)
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


def _load_readers(url_or_path: str, reporter: Reporter | None = None) -> list[Reader]:
    return load_plugins(Reader, "readers", url_or_path, reporter=reporter)
