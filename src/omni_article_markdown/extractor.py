from abc import ABC, abstractmethod
from dataclasses import dataclass
from bs4 import BeautifulSoup, element

from .utils import Constants, extract_article_from_soup


@dataclass
class Article:
    title: str
    description: str
    body: element.Tag


class Extractor(ABC):

    def __init__(self):
        self.tags_to_clean = Constants.TAGS_TO_CLEAN
        self.attrs_to_clean = Constants.ATTRS_TO_CLEAN

    def extract(self, soup: BeautifulSoup) -> Article | None:
        if self.can_handle(soup):
            article_container = self.article_container()
            if isinstance(article_container, tuple):
                article_container = [article_container]
            for container in article_container:
                article_tag: element.Tag = extract_article_from_soup(soup, container)
                if article_tag:
                    for tag in article_tag.find_all():
                        if any(cond(tag) for cond in self.tags_to_clean):
                            tag.decompose()
                            continue
                        if tag.attrs:
                            if any(cond(tag) for cond in self.attrs_to_clean):
                                tag.decompose()
                    title = self.extract_title(soup)
                    description = self.extract_description(soup)
                    return Article(title=title, description=description, body=article_tag)
        return None

    @abstractmethod
    def can_handle(self, soup: BeautifulSoup) -> bool:
        ...

    @abstractmethod
    def article_container(self) -> tuple | list:
        ...

    def extract_title(self, soup: BeautifulSoup) -> str:
        og_title_tag = soup.find("meta", {"property": "og:title"})
        title = og_title_tag["content"].strip() if og_title_tag and "content" in og_title_tag.attrs else None
        if title:
            return title
        # h1 = article.find("h1", {"class": "wp-block-post-title"})
        title_tag = soup.title
        title = title_tag.text.strip() if title_tag else None
        # 确保 title 不为 None
        return title or "Untitled"

    def extract_description(self, soup: BeautifulSoup) -> str | None:
        og_desc_tag = soup.find("meta", {"property": "og:description"})
        return og_desc_tag["content"].strip() if og_desc_tag and "content" in og_desc_tag.attrs else None

    def get_og_site_name(self, soup: BeautifulSoup) -> str | None:
        site_name_tag = soup.find("meta", {"property": "og:site_name"})
        return site_name_tag["content"].strip() if site_name_tag and site_name_tag.has_attr("content") else None

class DefaultExtractor(Extractor):
    def can_handle(self, soup: BeautifulSoup) -> bool:
        return True

    def article_container(self) -> tuple | list:
        return Constants.ARTICLE_CONTAINERS
