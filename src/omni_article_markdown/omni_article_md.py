import importlib
import pkgutil
from dataclasses import dataclass
from pathlib import Path

from .extractor import Article, DefaultExtractor, Extractor
from .parser import HtmlMarkdownParser
from .readers import ReaderFactory
from .utils import to_snake_case


@dataclass
class ReaderContext:
    extractor: Extractor | None
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

    def __init__(self, url_or_path: str):
        self.url_or_path = url_or_path

    def parse(self) -> ParserContext:
        reader_ctx = self._read_html(self.url_or_path)
        extractor_ctx = self._extract_article(reader_ctx)
        parser_ctx = self._parse_html(extractor_ctx)
        return parser_ctx

    def save(self, ctx: ParserContext, save_path: str = "") -> str:
        save_path = save_path or self.DEFAULT_SAVE_PATH
        file_path = Path(save_path)
        if file_path.is_dir():
            filename = f"{to_snake_case(ctx.title)}.md"
            file_path = file_path / filename
        with file_path.open("w", encoding="utf-8") as f:
            f.write(ctx.markdown)
        return str(file_path.resolve())

    def _read_html(self, url_or_path: str) -> ReaderContext:
        reader = ReaderFactory.create(url_or_path)
        raw_html = reader.read()
        return ReaderContext(extractor=reader.extractor(), raw_html=raw_html)

    def _extract_article(self, ctx: ReaderContext) -> ExtractorContext:
        if ctx.extractor:
            article = ctx.extractor.extract(ctx.raw_html)
        else:
            for extract in load_extractors():
                article = extract.extract(ctx.raw_html)
                if article:
                    break
            else:
                article = DefaultExtractor().extract(ctx.raw_html)
        if not article:
            raise ValueError("Failed to extract article content.")
        return ExtractorContext(article=article)

    def _parse_html(self, ctx: ExtractorContext) -> ParserContext:
        parser = HtmlMarkdownParser(ctx.article)
        result = parser.parse()
        return ParserContext(title=result[0], markdown=result[1])


def load_extractors(package_name="extractors") -> list[Extractor]:
    extractors_package = Path(__file__).parent / package_name
    extractors = []
    for loader, module_name, is_pkg in pkgutil.iter_modules([extractors_package.resolve()]):
        module = importlib.import_module(f"omni_article_markdown.{package_name}.{module_name}")
        for attr in dir(module):
            cls = getattr(module, attr)
            if isinstance(cls, type) and issubclass(cls, Extractor) and cls is not Extractor:
                extractors.append(cls())
    return extractors
