from ..extractor import Extractor


class WechatGZHExtractor(Extractor):
    """
    微信公众号
    """

    def extract(self) -> tuple:
        return ("div", {"id": "page-content"})
