from pathlib import Path

from .readers import ReaderFactory
from .html_md_parser import HtmlMarkdownParser
from .utils import to_snake_case


class OmniArticleMarkdown:

    DEFAULT_SAVE_PATH = "./"

    def __init__(self, url_or_path: str):
        self.url_or_path = url_or_path
        self.title = None
        self.markdown = None
        self.save_path = None

    def parse(self) -> str:
        reader = ReaderFactory.create(self.url_or_path)
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
        self.save_path = str(file_path.resolve())
