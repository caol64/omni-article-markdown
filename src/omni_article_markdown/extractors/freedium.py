from bs4 import BeautifulSoup
from ..extractor import Extractor


class FreediumExtractor(Extractor):
    """
    freedium.cfd
    """

    def can_handle(self, soup: BeautifulSoup) -> bool:
        title_tag = soup.title
        title = title_tag.text.strip() if title_tag else None
        return title and title.endswith(" - Freedium")

    def article_container(self) -> tuple:
        return ("div", {"class": "main-content"})

    def extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find("h1")
        title = title_tag.text.strip()
        title_tag.decompose()
        return title

    def extract_description(self, soup: BeautifulSoup) -> str:
        description_tag = soup.find("h2")
        description = description_tag.text.strip()
        description_tag.decompose()
        return description
