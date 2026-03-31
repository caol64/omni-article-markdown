from typing import override

from ..launch_playwright import create_stealth_page
from ..reader import Reader


class ScrollableBrowserReader(Reader):
    @override
    def read(self) -> str:
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            import time

            try:
                page.goto(self.url_or_path, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_selector('[data-testid="tweet"], article', timeout=30000)
                # 滚动页面以触发懒加载
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(5)
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(3)
                return page.content()
            except Exception as e:
                raise Exception(f"页面加载失败: {str(e)}")

    @override
    def can_handle(self) -> bool:
        return "x.com" in self.url_or_path
