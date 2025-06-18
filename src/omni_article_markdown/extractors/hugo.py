from ..extractor import Extractor


class HugoExtractor(Extractor):
    """
    Hugo博客
    """

    def extract(self) -> tuple:
        return ("div", {"class": "post-content"})
