from typing import override

from ..launch_playwright import create_stealth_page
from ..reader import Reader


class BrowserReader(Reader):
    TARGET_HOSTS = {
        "https://developer.apple.com/documentation/": 'main[class="main"]',
        "https://www.infoq.cn/": 'div[class="article-content-wrap"]',
        "https://pcsx2.net/": "body",
        "https://baijiahao.baidu.com/": "body",
        "https://www.toutiao.com/article": 'div[class="article-content"]',
        "https://medium.com": "article",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def read(self) -> str:
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            try:
                page.goto(self.url_or_path, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_selector(self._get_matched_selector(), timeout=30000)
                return page.content()
            except Exception as e:
                raise Exception(f"页面加载失败: {str(e)}")

    @override
    def can_handle(self) -> bool:
        return self._get_matched_selector() is not None

    def _get_matched_selector(self) -> str | None:
        for host, selector in self.TARGET_HOSTS.items():
            if self.url_or_path.startswith(host):
                return selector
        return None
