from typing import override

from ..launch_playwright import create_stealth_page
from .browser import BrowserReader


class ScrollableBrowserReader(BrowserReader):
    TARGET_HOSTS = {
        "https://x.com": 'article[data-testid="tweet"]',
    }

    @override
    def read(self) -> str:
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            try:
                page.goto(self.url_or_path, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_selector(self._get_matched_selector(), timeout=30000)
                # 滚动页面以触发懒加载
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(1000)
                return page.content()
            except Exception as e:
                raise Exception(f"页面加载失败: {str(e)}")
