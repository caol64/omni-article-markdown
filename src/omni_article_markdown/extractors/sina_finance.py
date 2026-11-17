from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import get_og_url


class SinaFinanceExtractor(Extractor):
    """
    新浪财经 (finance.sina.com.cn)
    """

    @override
    def can_handle(self) -> bool:
        return get_og_url(self.soup).startswith("https://finance.sina.com.cn/") and bool(
            self.soup.find("div", id="artibody")
        )

    @override
    def article_container(self) -> tuple:
        return ("div", {"id": "artibody"})

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            # 文末 “海量资讯、精准解读，尽在新浪财经APP” 二维码块
            lambda el: "class" in el.attrs and "appendQr_wrap" in el.attrs["class"],
            # 正文内嵌的行情/开户导流组件
            lambda el: (
                "class" in el.attrs
                and any(c in ("ct_hqimg", "hqimg_wrapper", "app-kaihu-qr") for c in el.attrs["class"])
            ),
        ]
