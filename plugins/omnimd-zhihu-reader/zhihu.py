import sys
from importlib import resources
from runpy import run_module
from typing import override

import requests
from playwright.sync_api import Browser, Cookie, Playwright, sync_playwright

from omni_article_markdown.hookspecs import ReaderPlugin, hookimpl
from omni_article_markdown.store import Store
from omni_article_markdown.utils import REQUEST_HEADERS


class ZhihuPlugin(ReaderPlugin):
    @override
    def can_handle(self, url: str) -> bool:
        return "zhihu.com" in url

    @override
    def read(self, url: str) -> str:
        store = Store()
        cookies_raw = store.load("zhihu_cookies")

        if not cookies_raw:
            print("未找到知乎登录信息，尝试模拟登录...")
            cookies_raw = self._get_zhihu_cookies(url)
            if not cookies_raw:
                raise Exception("无法获取知乎登录信息")

        cookies = self._convert_playwright_cookies_to_requests_dict(cookies_raw)
        response = requests.get(url, headers=REQUEST_HEADERS, cookies=cookies)

        # 如果初始请求失败，则尝试重新获取 cookie 并重试
        if response.status_code == 403:
            print("Cookie 失效，重新模拟登录知乎...")
            cookies_raw = self._get_zhihu_cookies(url)
            if not cookies_raw:
                raise Exception("重新模拟登录失败，无法访问知乎内容")
            cookies = self._convert_playwright_cookies_to_requests_dict(cookies_raw)
            response = requests.get(url, headers=REQUEST_HEADERS, cookies=cookies)

        response.encoding = "utf-8"
        return response.text

    def _get_zhihu_cookies(self, url: str) -> list[Cookie]:
        def try_launch_browser(p: Playwright) -> Browser:
            try:
                return p.chromium.launch(headless=True)
            except Exception as e:
                # Playwright not installed or browser missing
                if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
                    print("[INFO] Chromium not installed, installing with 'playwright install chromium'...")
                    original_argv = sys.argv
                    args = ["playwright", "install", "chromium"]
                    sys.argv = args
                    run_module("playwright", run_name="__main__")
                    sys.argv = original_argv
                    # Try again
                    return p.chromium.launch(headless=True)
                raise  # re-raise other exceptions

        with sync_playwright() as p:
            browser = try_launch_browser(p)
            context = browser.new_context(
                user_agent=REQUEST_HEADERS["User-Agent"],
                java_script_enabled=True,
                extra_http_headers=REQUEST_HEADERS,
            )
            with resources.path("omni_article_markdown.libs", "stealth.min.js") as js_path:
                context.add_init_script(path=str(js_path))
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            cookies = context.cookies()
            store = Store()
            store.save("zhihu_cookies", cookies)
            page.close()
            context.close()
            browser.close()
            return cookies

    def _convert_playwright_cookies_to_requests_dict(self, playwright_cookies: list[Cookie]) -> dict[str, str]:
        requests_cookies = {}
        for cookie in playwright_cookies:
            requests_cookies[cookie.get("name")] = cookie.get("value")
        return requests_cookies


@hookimpl
def get_custom_reader(url: str) -> ReaderPlugin | None:
    plugin_instance = ZhihuPlugin()
    if plugin_instance.can_handle(url):
        return plugin_instance
    return None
