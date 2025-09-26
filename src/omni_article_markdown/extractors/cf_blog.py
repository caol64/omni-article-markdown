from bs4 import BeautifulSoup
from ..extractor import Extractor


class CloudflareBlogxtractor(Extractor):
    """
    blog.cloudflare.com
    """

    def can_handle(self, soup: BeautifulSoup) -> bool:
        canonical_tag = soup.find("link", {"rel": "canonical"})
        canonical = canonical_tag["href"].strip() if canonical_tag and canonical_tag.has_attr("href") else None
        return canonical and canonical.startswith("https://blog.cloudflare.com")

    def article_container(self) -> tuple:
        return ("section", {"class": "post-full-content"})
