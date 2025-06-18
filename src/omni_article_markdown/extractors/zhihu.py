from ..extractor import Extractor


class ZhihuExtractor(Extractor):
    """
    知乎专栏
    """

    def extract(self) -> tuple:
        return ("div", {"class": "Post-RichText"})
