from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

from bs4 import BeautifulSoup
from bs4.element import Tag

from .utils import Constants, filter_tag, get_attr_text


@dataclass
class Article:
    title: str
    og_url: str | None
    description: str | None
    body: Tag


class Extractor(ABC):
    def __init__(self):
        self.tags_to_clean = Constants.TAGS_TO_CLEAN
        self.attrs_to_clean = Constants.ATTRS_TO_CLEAN

    def extract(self, raw_html: str) -> Article | None:
        soup = BeautifulSoup(raw_html, "html5lib")
        if self.can_handle(soup):
            og_url = get_og_url(soup)
            article_container = self.article_container()
            if isinstance(article_container, tuple):
                article_container = [article_container]
            for container in article_container:
                article_tag = extract_article_from_soup(soup, container)
                if article_tag:
                    # print(f"Using extractor: {self.__class__.__name__}")
                    h1 = article_tag.find("h1")
                    if h1:
                        h1.decompose()
                    for el in article_tag.find_all():
                        tag = filter_tag(el)
                        if tag:
                            if any(cond(tag) for cond in self.tags_to_clean):
                                tag.decompose()
                                continue
                            if tag.attrs:
                                if any(cond(tag) for cond in self.attrs_to_clean):
                                    tag.decompose()
                    title = self.extract_title(soup)
                    description = self.extract_description(soup)
                    return Article(
                        title=title, og_url=og_url, description=description, body=article_tag
                    )
        return None

    @abstractmethod
    def can_handle(self, soup: BeautifulSoup) -> bool: ...

    @abstractmethod
    def article_container(self) -> tuple | list: ...

    def extract_title(self, soup: BeautifulSoup) -> str:
        return get_og_title(soup) or get_title(soup)

    def extract_description(self, soup: BeautifulSoup) -> str:
        return get_og_description(soup)

class DefaultExtractor(Extractor):
    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return True

    @override
    def article_container(self) -> tuple | list:
        return Constants.ARTICLE_CONTAINERS



def extract_article_from_soup(soup: BeautifulSoup, template: tuple) -> Tag | None:
    if template[1] is not None:
        result = soup.find(template[0], attrs=template[1])
    else:
        result = soup.find(template[0])
    return filter_tag(result)


def get_og_url(soup: BeautifulSoup) -> str:
    og_tag = filter_tag(soup.find("meta", {"property": "og:url"}))
    return get_tag_text(og_tag, "content")


def get_og_site_name(soup: BeautifulSoup) -> str:
    og_tag = filter_tag(soup.find("meta", {"property": "og:site_name"}))
    return get_tag_text(og_tag, "content")


def get_og_description(soup: BeautifulSoup) -> str:
    og_tag = filter_tag(soup.find("meta", {"property": "og:description"}))
    return get_tag_text(og_tag, "content")


def get_canonical_url(soup: BeautifulSoup) -> str:
    canonical_tag = filter_tag(soup.find("link", {"rel": "canonical"}))
    return get_tag_text(canonical_tag, "href")


def is_matched_canonical(url: str, soup: BeautifulSoup) -> bool:
    canonical = get_canonical_url(soup)
    if not canonical:
        return False
    return canonical.startswith(url)


def get_og_title(soup: BeautifulSoup) -> str:
    og_tag = filter_tag(soup.find("meta", {"property": "og:title"}))
    return get_tag_text(og_tag, "content")


def get_tag_text(tag: Tag | None, attr: str) -> str:
    if tag is not None and tag.has_attr(attr):
        el = tag[attr]
        return get_attr_text(el)
    return ""


def get_title(soup: BeautifulSoup) -> str:
    title_tag = soup.title
    return title_tag.get_text(strip=True) if title_tag else ""
