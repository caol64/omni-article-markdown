from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup

from .extractor import Article, ExtractorFactory
from .parser import HtmlMarkdownParser
from .reader import ReaderFactory
from .reporter import Reporter
from .utils import to_snake_case


@dataclass
class ReaderContext:
    raw_html: str


@dataclass
class ExtractorContext:
    article: Article


@dataclass
class ParserContext:
    title: str
    markdown: str


class OmniArticleMarkdown:
    DEFAULT_SAVE_PATH = "./"

    def __init__(self, url_or_path: str, reporter: Reporter | None = None, verify_ssl: bool = True):
        self.url_or_path = url_or_path
        self.reporter = reporter
        self.verify_ssl = verify_ssl
        self.parser_ctx: ParserContext | None = None

    def parse(self):
        reader_ctx = self._read_html(self.url_or_path)
        extractor_ctx = self._extract_article(reader_ctx)
        self.parser_ctx = self._parse_html(extractor_ctx)

    def result(self):
        if not self.parser_ctx:
            raise ValueError("No parsed content available. Please call parse() first.")
        return self.parser_ctx.markdown

    def save(self, save_path: str = "") -> str:
        if not self.parser_ctx:
            raise ValueError("No parsed content to save. Please call parse() first.")
        save_path = save_path or self.DEFAULT_SAVE_PATH
        file_path = Path(save_path)
        if file_path.is_dir():
            filename = f"{to_snake_case(self.parser_ctx.title)}.md"
            file_path = file_path / filename
        with file_path.open("w", encoding="utf-8") as f:
            f.write(self.parser_ctx.markdown)
        return str(file_path.resolve())

    def _read_html(self, url_or_path: str) -> ReaderContext:
        reader = ReaderFactory.create(url_or_path, reporter=self.reporter, verify_ssl=self.verify_ssl)
        raw_html = reader.read()
        return ReaderContext(raw_html)

    def _extract_article(self, ctx: ReaderContext) -> ExtractorContext:
        soup = BeautifulSoup(ctx.raw_html, "html5lib")
        extract = ExtractorFactory.create(soup)
        article = extract.extract()
        if not article:
            raise ValueError("Failed to extract article content.")
        return ExtractorContext(article)

    def _parse_html(self, ctx: ExtractorContext) -> ParserContext:
        parser = HtmlMarkdownParser(ctx.article)
        result = parser.parse()
        return ParserContext(title=result[0], markdown=result[1])
