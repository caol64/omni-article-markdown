from typing import override

from ..launch_playwright import create_stealth_page
from ..reader import Reader


class FeishuReader(Reader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def read(self) -> str:
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            try:
                page.goto(self.url_or_path, wait_until="domcontentloaded", timeout=45000)
                # page.wait_for_selector('div[class="page-block-children"]', timeout=30000)
                page.wait_for_timeout(5000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(1000)
                return page.content()
            except Exception as e:
                raise Exception(f"页面加载失败: {str(e)}")

    @override
    def can_handle(self) -> bool:
        return ".feishu.cn/wiki/" in self.url_or_path

