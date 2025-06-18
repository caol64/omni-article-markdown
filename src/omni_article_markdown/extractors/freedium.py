from ..extractor import Extractor


class FreediumExtractor(Extractor):
    """
    freedium.cfd
    """

    def extract(self) -> tuple:
        return ("div", {"class": "main-content"})
