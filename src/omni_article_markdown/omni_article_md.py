from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag

from .extractor import Article, ExtractorFactory
from .markdown_detector import extract_markdown_title, looks_like_markdown
from .parser import HtmlMarkdownParser
from .reader import ReaderFactory
from .reporter import Reporter
from .utils import to_snake_case


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
        raw = self._read(self.url_or_path)
        # 纯 Markdown 源（如 raw.githubusercontent.com）不经 HTML 解析，原样透传
        if looks_like_markdown(raw):
            if self.reporter:
                self.reporter("检测到 Markdown 源，已原样输出（跳过转换）")
            self.parser_ctx = self._passthrough_markdown(raw)
            return
        extractor_ctx = self._extract_article(raw)
        self.parser_ctx = self._parse_html(extractor_ctx)

    def _passthrough_markdown(self, raw: str) -> ParserContext:
        # 原文逐字节保留，仅去掉尾部空白并保证单个结尾换行
        return ParserContext(title=extract_markdown_title(raw), markdown=raw.rstrip() + "\n")

    def result(self):
        if not self.parser_ctx:
            raise ValueError("No parsed content available. Please call parse() first.")
        return self.parser_ctx.markdown

    def save(self, save_path: str = "", markdown: str | None = None) -> str:
        if not self.parser_ctx:
            raise ValueError("No parsed content to save. Please call parse() first.")
        save_path = save_path or self.DEFAULT_SAVE_PATH
        file_path = Path(save_path)
        if file_path.is_dir():
            filename = f"{to_snake_case(self.parser_ctx.title)}.md"
            file_path = file_path / filename
        with file_path.open("w", encoding="utf-8") as f:
            f.write(markdown if markdown is not None else self.parser_ctx.markdown)
        return str(file_path.resolve())

    def _read(self, url_or_path: str) -> str:
        reader = ReaderFactory.create(url_or_path, reporter=self.reporter, verify_ssl=self.verify_ssl)
        return reader.read()

    def _extract_article(self, ctx: str) -> ExtractorContext:
        soup = BeautifulSoup(ctx, "html5lib")
        extract = ExtractorFactory.create(soup)
        article = extract.extract()
        if not article or not self._has_body_content(article.body):
            raise ValueError("Failed to extract article content.")
        return ExtractorContext(article)

    @staticmethod
    def _has_body_content(body: Tag | str) -> bool:
        if isinstance(body, str):
            return bool(body.strip())
        return bool(body.get_text(strip=True))

    def _parse_html(self, ctx: ExtractorContext) -> ParserContext:
        parser = HtmlMarkdownParser(ctx.article)
        result = parser.parse()
        # 非文章页面（如纯文本 404）常无标题：此时内容不可用
        if not result[0].strip():
            raise ValueError("Failed to extract article content (no title found).")
        return ParserContext(title=result[0], markdown=result[1])
