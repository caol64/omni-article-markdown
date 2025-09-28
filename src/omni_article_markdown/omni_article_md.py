from dataclasses import dataclass
import importlib
from pathlib import Path
import pkgutil
from typing import Optional

from bs4 import BeautifulSoup

from .extractor import Article, DefaultExtractor, Extractor
from .readers import Reader, ReaderFactory
from .html_md_parser import HtmlMarkdownParser
from .utils import to_snake_case


@dataclass
class Context:
    url_or_path: str
    reader: Optional[Reader] = None
    extractor: Optional[Extractor] = None
    raw_html: Optional[str] = None
    og_url: Optional[str] = None
    article: Optional[Article] = None
    title: Optional[str] = None
    markdown: Optional[str] = None


class OmniArticleMarkdown:

    DEFAULT_SAVE_PATH = "./"

    def __init__(self, url_or_path: str):
        self.url_or_path = url_or_path
        self.title = None
        self.markdown = None
        self.save_path = None

    def parse(self) -> str:
        context = Context(url_or_path=self.url_or_path)
        steps = [
            self._create_reader,
            self._read_html,
            self._extract_article,
            self._parse_html,
        ]
        for step in steps:
            step(context)
        self.title = context.title
        self.markdown = context.markdown
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

    def _create_reader(self, ctx: Context):
        ctx.reader = ReaderFactory.create(ctx.url_or_path)
        ctx.extractor = ctx.reader.extractor()

    def _read_html(self, ctx: Context):
        ctx.raw_html = ctx.reader.read()
        print(ctx.raw_html)

    def _extract_article(self, ctx: Context):
        soup = BeautifulSoup(ctx.raw_html, "html5lib")
        og_url = soup.find("meta", {"property": "og:url"})
        ctx.og_url = og_url["content"].strip() if og_url and "content" in og_url.attrs else None
        if ctx.extractor:
            ctx.article = ctx.extractor.extract(soup)
        else:
            for extract in load_extractors():
                article = extract.extract(soup)
                if article:
                    ctx.article = article
                    break
            else:
                ctx.article = DefaultExtractor().extract(soup)

    def _parse_html(self, ctx: Context):
        parser = HtmlMarkdownParser(ctx.article, ctx.og_url)
        ctx.title, ctx.markdown = parser.parse()


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
