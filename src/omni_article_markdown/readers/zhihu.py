from typing import Any, override

from ..launch_playwright import create_stealth_page
from ..reader import Reader
from ..store import Store
from ..utils import convert_cookies_to_requests_dict


class ZhihuReader(Reader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = Store()

    @override
    def read(self) -> str:
        cookies_raw = self.store.load("zhihu_cookies")

        if not cookies_raw:
            self.report("未找到知乎Cookies，准备启动模拟登录...")
            cookies_raw = self._get_zhihu_cookies(self.url_or_path)
            if not cookies_raw:
                raise Exception("无法获取知乎Cookies，抓取失败")

        cookies = convert_cookies_to_requests_dict(cookies_raw)
        response = self.session.get(self.url_or_path, cookies=cookies)
        response.encoding = "utf-8"

        # 检查是否失效或被反爬拦截
        if response.status_code == 403:
            self.report("知乎Cookies已失效或触发风控，正在强制刷新...")
            cookies_raw = self._get_zhihu_cookies(self.url_or_path)
            if not cookies_raw:
                raise Exception("强制刷新Cookies失败")

            cookies = convert_cookies_to_requests_dict(cookies_raw)
            response = self.session.get(self.url_or_path, cookies=cookies)

        return response.text

    def _get_zhihu_cookies(self, url: str) -> list[dict[str, Any]]:
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                target_cookies = ["d_c0"]
                self.report(f"等待知乎生成关键Cookie({', '.join(target_cookies)})...")
                import json

                target_cookies_js = json.dumps(target_cookies)
                js_function = f"""
                () => {{
                    const targets = {target_cookies_js};
                    return targets.every(cookieName => document.cookie.includes(cookieName + '='));
                }}
                """
                page.wait_for_function(js_function, timeout=8000)
            except Exception as e:
                self.report(f"页面加载提示 (可能已成功获取 Cookie): {str(e)}")

            # 提取 Cookie
            raw_cookies = context.cookies()
            cookies: list[dict[str, Any]] = [dict(c) for c in raw_cookies]
            self.store.save("zhihu_cookies", cookies)
            self.report("成功获取并保存知乎Cookies")

            return cookies

    @override
    def can_handle(self) -> bool:
        return "zhihu.com" in self.url_or_path
