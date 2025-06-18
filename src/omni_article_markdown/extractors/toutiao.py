from ..extractor import Extractor


class ToutiaoExtractor(Extractor):
    """
    今日头条
    """

    def extract(self) -> tuple:
        return ("div", {"class": "article-content"})
