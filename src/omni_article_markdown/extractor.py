import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import final, override

from bs4 import BeautifulSoup
from bs4.element import Comment, Tag

from .article import Article
from .plugins import load_plugins
from .utils import filter_tag, get_attr_text, get_canonical_url, get_og_description, get_og_title, get_og_url, get_title

type TagPredicate = Callable[[Tag], bool]

TAGS_TO_CLEAN: list[TagPredicate] = [
    lambda el: el.name in ("style", "link", "button", "footer", "header"),
    lambda el: el.name == "script" and "src" not in el.attrs,
    lambda el: (
        el.name == "script"
        and el.has_attr("src")
        and not get_attr_text(el.attrs["src"]).startswith("https://gist.github.com")
    ),
]

ATTRS_TO_CLEAN: list[TagPredicate] = [
    lambda el: (
        "style" in el.attrs
        and re.search(r"display\s*:\s*none", get_attr_text(el.attrs.get("style")), re.IGNORECASE) is not None
    ),
    lambda el: "hidden" in el.attrs,
    lambda el: "class" in el.attrs and "katex-html" in el.attrs["class"],  # katex
]

ARTICLE_CONTAINERS = [("article", None), ("main", None), ("body", None)]


class Extractor(ABC):
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    @final
    def extract(self) -> Article | None:
        # print(f"Using extractor: {self.__class__.__name__}")
        self.pre_handle_soup()
        article_container = self.article_container()
        if isinstance(article_container, tuple):
            article_container = [article_container]
        for container in article_container:
            article = self.extract_article()
            if article:
                return article
            article_tag = self.extract_article_from_soup(container)
            if article_tag:
                for el in article_tag.find_all():
                    tag = filter_tag(el)
                    if tag:
                        if any(cond(tag) for cond in self.get_tags_to_clean()):
                            tag.decompose()
                            continue
                        if tag.attrs and any(cond(tag) for cond in self.get_attrs_to_clean()):
                            tag.decompose()
                for comment in article_tag.find_all(string=lambda text: isinstance(text, Comment)):
                    comment.extract()
                self.extract_img(article_tag)
                title = self.extract_title()
                description = self.extract_description()
                url = self.extract_url()
                article = Article(title=title, url=url, description=description, body=article_tag)
                self.remove_duplicate_titles(article)
                return article
        return None

    @abstractmethod
    def can_handle(self) -> bool: ...

    def get_tags_to_clean(self) -> list[Callable[[Tag], bool]]:
        return list(TAGS_TO_CLEAN)

    def get_attrs_to_clean(self) -> list[Callable[[Tag], bool]]:
        return list(ATTRS_TO_CLEAN)

    def article_container(self) -> tuple | list[tuple]:
        return ARTICLE_CONTAINERS

    def extract_title(self) -> str:
        return get_og_title(self.soup) or get_title(self.soup)

    def extract_description(self) -> str:
        return get_og_description(self.soup)

    def extract_url(self) -> str:
        return get_og_url(self.soup) or get_canonical_url(self.soup)

    def extract_img(self, element: Tag) -> Tag:
        return element

    def extract_article(self) -> Article | None:
        return None

    def pre_handle_soup(self):
        return

    def extract_article_from_soup(self, template: tuple) -> Tag | None:
        if template[1] is not None:
            result = self.soup.find(template[0], attrs=template[1])
        else:
            result = self.soup.find(template[0])
        return filter_tag(result)

    def remove_duplicate_titles(self, article: Article):
        if article.body and isinstance(article.body, Tag):
            first_h1 = article.body.find("h1")
            if first_h1:
                h1_text = first_h1.get_text(strip=True)
                if h1_text.lower() in article.title.lower():
                    article.title = h1_text
                    first_h1.decompose()


class ExtractorFactory:
    @staticmethod
    def create(soup: BeautifulSoup) -> Extractor:
        for extract in _load_extractors(soup):
            if extract.can_handle():
                return extract
        return DefaultExtractor(soup)


class DefaultExtractor(Extractor):
    @override
    def can_handle(self) -> bool:
        return True


def _load_extractors(soup: BeautifulSoup) -> list[Extractor]:
    return load_plugins(Extractor, "extractors", soup)
