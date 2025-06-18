from ..extractor import Extractor


class QuantamagazineExtractor(Extractor):
    """
    quantamagazine.org
    """

    def extract(self) -> tuple:
        return ("div", {"id": "postBody"})
