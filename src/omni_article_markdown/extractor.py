import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import override

from bs4 import BeautifulSoup
from bs4.element import Comment, Tag

from .utils import filter_tag, get_attr_text, get_canonical_url, get_og_description, get_og_title, get_og_url, get_title

TAGS_TO_CLEAN: list[Callable[[Tag], bool]] = [
    lambda el: el.name in ("style", "link", "button", "footer", "header", "aside"),
    lambda el: el.name == "script" and "src" not in el.attrs,
    lambda el: el.name == "script"
        and el.has_attr("src")
        and not get_attr_text(el.attrs["src"]).startswith("https://gist.github.com"),
]

ATTRS_TO_CLEAN: list[Callable[[Tag], bool]] = [
    lambda el: "style" in el.attrs
        and re.search(r"display\s*:\s*none", get_attr_text(el.attrs.get("style")), re.IGNORECASE) is not None,
    lambda el: "hidden" in el.attrs,
    lambda el: "class" in el.attrs and "katex-html" in el.attrs["class"],  # katex
]

ARTICLE_CONTAINERS = [("article", None), ("main", None), ("body", None)]


@dataclass
class Article:
    title: str
    url: str | None
    description: str | None
    body: Tag | str


class Extractor(ABC):
    def __init__(self):
        self.tags_to_clean = TAGS_TO_CLEAN
        self.attrs_to_clean = ATTRS_TO_CLEAN

    def extract(self, soup: BeautifulSoup) -> Article | None:
        if self.can_handle(soup):
            # print(f"Using extractor: {self.__class__.__name__}")
            soup = self.pre_handle_soup(soup)
            article_container = self.article_container()
            if isinstance(article_container, tuple):
                article_container = [article_container]
            for container in article_container:
                article = self.extract_article(soup)
                if article:
                    return article
                article_tag = extract_article_from_soup(soup, container)
                if article_tag:
                    for el in article_tag.find_all():
                        tag = filter_tag(el)
                        if tag:
                            if any(cond(tag) for cond in self.tags_to_clean):
                                tag.decompose()
                                continue
                            if tag.attrs and any(cond(tag) for cond in self.attrs_to_clean):
                                tag.decompose()
                    for comment in article_tag.find_all(string=lambda text: isinstance(text, Comment)):
                        comment.extract()
                    self.extract_img(article_tag)
                    title = self.extract_title(soup)
                    description = self.extract_description(soup)
                    url = self.extract_url(soup)
                    article = Article(title=title, url=url, description=description, body=article_tag)
                    remove_duplicate_titles(article)
                    return article
        return None

    @abstractmethod
    def can_handle(self, soup: BeautifulSoup) -> bool: ...

    @abstractmethod
    def article_container(self) -> tuple | list: ...

    def extract_title(self, soup: BeautifulSoup) -> str:
        return get_og_title(soup) or get_title(soup)

    def extract_description(self, soup: BeautifulSoup) -> str:
        return get_og_description(soup)

    def extract_url(self, soup: BeautifulSoup) -> str:
        return get_og_url(soup) or get_canonical_url(soup)

    def extract_img(self, element: Tag) -> Tag:
        return element

    def extract_article(self, soup: BeautifulSoup) -> Article | None:
        return None

    def pre_handle_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        return soup


class DefaultExtractor(Extractor):
    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return True

    @override
    def article_container(self) -> tuple | list:
        return ARTICLE_CONTAINERS


def extract_article_from_soup(soup: BeautifulSoup, template: tuple) -> Tag | None:
    if template[1] is not None:
        result = soup.find(template[0], attrs=template[1])
    else:
        result = soup.find(template[0])
    return filter_tag(result)


def remove_duplicate_titles(article: Article):
    if article.body and isinstance(article.body, Tag):
        first_h1 = article.body.find("h1")
        if first_h1:
            h1_text = first_h1.get_text(strip=True)
            if h1_text.lower() in article.title.lower():
                article.title = h1_text
                first_h1.decompose()
