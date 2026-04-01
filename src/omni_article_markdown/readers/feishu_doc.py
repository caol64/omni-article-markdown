from typing import override

from ..launch_playwright import create_stealth_page
from ..reader import Reader
from ..utils import clean_text


class FeishuDocReader(Reader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def read(self) -> str:
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            try:
                page.goto(self.url_or_path, wait_until="domcontentloaded", timeout=45000)
                js_function = """
                () => {{
                    return document.title.trim().endsWith(" - 飞书云文档");
                }}
                """
                page.wait_for_function(js_function, timeout=8000)
                return clean_text(page.content())
            except Exception as e:
                raise Exception(f"页面加载失败: {str(e)}")

    @override
    def can_handle(self) -> bool:
        return ".feishu.cn/docx/" in self.url_or_path
