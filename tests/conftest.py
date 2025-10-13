import pytest
from bs4 import BeautifulSoup

@pytest.fixture
def make_soup():
    def _make_soup(html: str, parser: str = "html.parser"):
        return BeautifulSoup(html, parser)
    return _make_soup
