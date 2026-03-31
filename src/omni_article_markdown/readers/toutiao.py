from typing import override

from ..launch_playwright import create_stealth_page
from ..reader import Reader


class ToutiaoReader(Reader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def read(self) -> str:
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            try:
                page.goto(self.url_or_path, wait_until="networkidle", timeout=45000)
                return page.content()
            except Exception as e:
                raise Exception(f"页面加载失败: {str(e)}")

    @override
    def can_handle(self) -> bool:
        return "toutiao.com" in self.url_or_path
