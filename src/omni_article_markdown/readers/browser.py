from typing import override

from ..launch_playwright import create_stealth_page
from ..reader import Reader

TARGET_HOSTS = [
    "https://developer.apple.com/documentation/",
    "https://www.infoq.cn/",
    "https://pcsx2.net/",
    "https://baijiahao.baidu.com/",
    "https://www.snowflake.com/en/blog/",
    "https://www.toutiao.com/article",
]


class BrowserReader(Reader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def read(self) -> str:
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            try:
                page.goto(self.url_or_path, wait_until="domcontentloaded", timeout=45000)
                return page.content()
            except Exception as e:
                raise Exception(f"页面加载失败: {str(e)}")

    @override
    def can_handle(self) -> bool:
        return any(self.url_or_path.startswith(host) for host in TARGET_HOSTS)
