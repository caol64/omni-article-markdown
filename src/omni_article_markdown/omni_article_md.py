from pathlib import Path
import requests

from .html_md_parser import HtmlMarkdownParser
from .utils import to_snake_case


class HtmlReader:

    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Priority": "u=0, i",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }
    def __init__(self, url_or_path: str):
        self.url_or_path = url_or_path

    def read(self) -> str:
        if self.url_or_path.startswith("http"):
            response = requests.get(self.url_or_path, headers=HtmlReader.REQUEST_HEADERS)
            response.encoding = "utf-8"
            return response.text
        else:
            with open(self.url_or_path, "r") as f:
                return f.read()


class OmniArticleMarkdown:

    DEFAULT_SAVE_PATH = "./"

    def __init__(self, url_or_path: str):
        self.url_or_path = url_or_path
        self.title = None
        self.markdown = None

    def parse(self) -> str:
        reader = HtmlReader(self.url_or_path)
        raw_html = reader.read()
        html_arser = HtmlMarkdownParser(raw_html)
        self.title, self.markdown = html_arser.parse()
        return self.markdown

    def save(self, save_path: str = None):
        save_path = save_path or self.DEFAULT_SAVE_PATH
        file_path = Path(save_path)
        if file_path.is_dir():
            filename = f"{to_snake_case(self.title)}.md"
            file_path = file_path / filename 
        with file_path.open("w", encoding="utf-8") as f:
            f.write(self.markdown)