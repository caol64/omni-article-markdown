from bs4 import BeautifulSoup
from ..extractor import Extractor


class ToutiaoExtractor(Extractor):
    """
    今日头条
    """

    def can_handle(self, soup: BeautifulSoup) -> bool:
        title_tag = soup.title
        title = title_tag.text.strip() if title_tag else None
        return title and title.endswith(" - 今日头条")

    def article_container(self) -> tuple:
        return ("div", {"class": "article-content"})
