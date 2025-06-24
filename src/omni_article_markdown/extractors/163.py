from bs4 import BeautifulSoup
from ..extractor import Extractor


class Netease163Extractor(Extractor):
    """
    163.com
    """

    def can_handle(self, soup: BeautifulSoup) -> bool:
        canonical_tag = soup.find("link", {"rel": "canonical"})
        canonical = canonical_tag["href"].strip() if canonical_tag and canonical_tag.has_attr("href") else None
        return canonical and canonical.startswith("https://www.163.com")

    def article_container(self) -> tuple:
        return ("div", {"class": "post_body"})
