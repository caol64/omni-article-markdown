from ..extractor import Extractor


class Netease163Extractor(Extractor):
    """
    163.com
    """

    def extract(self) -> tuple:
        return ("div", {"class": "post_content"})
