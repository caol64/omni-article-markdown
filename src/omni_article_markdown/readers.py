from typing import Protocol

from .hookspecs import ReaderPlugin
from .plugins import pm
from .utils import REQUEST_HEADERS

import requests


class Reader(Protocol):
    def read(self) -> str:
        ...


class ReaderFactory:
    @staticmethod
    def create(url_or_path: str) -> Reader:
        custom_plugin_reader = pm.hook.get_custom_reader(url=url_or_path)
        if custom_plugin_reader:
            class PluginReaderAdapter(Reader):
                def __init__(self, plugin: ReaderPlugin, url: str):
                    self.plugin = plugin
                    self.url = url
                def read(self) -> str:
                    return self.plugin.read(self.url)
            return PluginReaderAdapter(custom_plugin_reader, url_or_path)
        if url_or_path.startswith("http"):
            return HtmlReader(url_or_path)
        else:
            return FileReader(url_or_path)


class HtmlReader(Reader):
    def __init__(self, url_or_path: str):
        self.url_or_path = url_or_path

    def read(self) -> str:
        # print(f"Using default HtmlReader for: {self.url_or_path}")
        response = requests.get(self.url_or_path, headers=REQUEST_HEADERS)
        response.encoding = "utf-8"
        return response.text


class FileReader(Reader):
    def __init__(self, url_or_path: str):
        self.url_or_path = url_or_path

    def read(self) -> str:
        with open(self.url_or_path, "r", encoding="utf8") as f:
            return f.read()
