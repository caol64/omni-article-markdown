from abc import ABC, abstractmethod
from pathlib import Path
from typing import override

from .http_client import get_session
from .plugins import load_plugins
from .reporter import Reporter


class Reader(ABC):
    def __init__(self, url_or_path: str, reporter: Reporter | None = None, verify_ssl: bool = True):
        self.url_or_path = url_or_path
        self.reporter = reporter
        self.verify_ssl = verify_ssl

        self.session = get_session(verify_ssl=self.verify_ssl)

    @abstractmethod
    def read(self) -> str: ...

    @abstractmethod
    def can_handle(self) -> bool: ...

    def report(self, message: str):
        if self.reporter:
            self.reporter(message)


class ReaderFactory:
    @staticmethod
    def create(url_or_path: str, reporter: Reporter | None = None, verify_ssl: bool = True) -> Reader:
        if url_or_path.startswith("http"):
            for reader in _load_readers(url_or_path, reporter=reporter, verify_ssl=verify_ssl):
                if reader.can_handle():
                    return reader
            return HtmlReader(url_or_path, reporter=reporter, verify_ssl=verify_ssl)
        file_reader = FileReader(url_or_path, reporter=reporter)
        if file_reader.can_handle():
            return file_reader
        raise ValueError(f"No suitable reader found for: {url_or_path}")


class HtmlReader(Reader):
    @override
    def read(self) -> str:
        response = self.session.get(self.url_or_path)
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


def _load_readers(url_or_path: str, reporter: Reporter | None = None, verify_ssl: bool = True) -> list[Reader]:
    return load_plugins(Reader, "readers", url_or_path, reporter=reporter, verify_ssl=verify_ssl)
