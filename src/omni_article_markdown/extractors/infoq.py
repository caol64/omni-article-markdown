from bs4 import BeautifulSoup
from ..extractor import Extractor


class InfoQExtractor(Extractor):
    """
    www.infoq.com
    """

    def can_handle(self, soup: BeautifulSoup) -> bool:
        canonical_tag = soup.find("link", {"rel": "canonical"})
        canonical = canonical_tag["href"].strip() if canonical_tag and canonical_tag.has_attr("href") else None
        return canonical and canonical.startswith("https://www.infoq.com")

    def article_container(self) -> tuple:
        return ("div", {"class": "article__data"})
