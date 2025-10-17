from typing import override
from bs4 import BeautifulSoup

from ..extractor import Extractor
from ..utils import filter_tag


class Netease163Extractor(Extractor):
    """
    百家号
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        tag1 = filter_tag(soup.find("div", {"data-testid": "article"}))
        tag2 = filter_tag(soup.find("span", {"class": "bjh-p"}))
        return tag1 is not None and tag2 is not None

    @override
    def article_container(self) -> tuple:
        return ("div", {"data-testid": "article"})

    @override
    def pre_handle_soup(self, soup: BeautifulSoup):
        for tag in soup.find_all("span", {"class": "bjh-p"}):
            span_tag = filter_tag(tag)
            if span_tag:
                span_tag.name = "p"
        # for tag in soup.find_all("img"):
        #     tag.wrap(soup.new_tag("p"))
