import sys
from typing import Optional, Any
from omni_article_markdown.hookspecs import hookimpl, ReaderPlugin
from omni_article_markdown.utils import REQUEST_HEADERS
from omni_article_markdown.store import Store
from playwright.sync_api import sync_playwright
from runpy import run_module

import importlib.resources
import requests


class ToutiaoReader(ReaderPlugin):
    def can_handle(self, url: str) -> bool:
        return "toutiao.com" in url

    def read(self, url: str) -> str:
        store = Store()
        cookies_raw = store.load("toutiao_cookies")

        if not cookies_raw:
            print("未找到头条登录信息，尝试模拟登录...")
            cookies_raw = self._get_toutiao_cookies(url)
            if not cookies_raw:
                raise Exception("无法获取头条登录信息")

        cookies = self._convert_playwright_cookies_to_requests_dict(cookies_raw)
        response = requests.get(url, headers=REQUEST_HEADERS, cookies=cookies)
        response.encoding = "utf-8"
        html = response.text

        # 如果初始请求失败，则尝试重新获取 cookie 并重试
        if "您需要允许该网站执行 JavaScript" in html:
            print("Cookie 失效，重新模拟登录头条...")
            cookies_raw = self._get_toutiao_cookies(url)
            if not cookies_raw:
                raise Exception("重新模拟登录失败，无法访问头条内容")
            cookies = self._convert_playwright_cookies_to_requests_dict(cookies_raw)
            response = requests.get(url, headers=REQUEST_HEADERS, cookies=cookies)

        response.encoding = "utf-8"
        return response.text

    def _get_toutiao_cookies(self, url: str) -> list[dict[str, Any]]:
        def try_launch_browser(p):
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
                else:
                    raise  # re-raise other exceptions
        with sync_playwright() as p:
            browser = try_launch_browser(p)
            context = browser.new_context(
                user_agent=REQUEST_HEADERS["User-Agent"],
                java_script_enabled=True,
                extra_http_headers=REQUEST_HEADERS,
            )
            with importlib.resources.path("omni_article_markdown.libs", "stealth.min.js") as js_path:
                context.add_init_script(path=str(js_path))
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            cookies = context.cookies()
            store = Store()
            store.save("toutiao_cookies", cookies)
            page.close()
            context.close()
            browser.close()
            return cookies

    def _convert_playwright_cookies_to_requests_dict(self, playwright_cookies: list[dict[str, Any]]) -> dict[str, str]:
        requests_cookies = {}
        for cookie in playwright_cookies:
            requests_cookies[cookie['name']] = cookie['value']
        return requests_cookies

# 实例化插件
toutiao_plugin_instance = ToutiaoReader()

@hookimpl
def get_custom_reader(url: str) -> Optional[ReaderPlugin]:
    if toutiao_plugin_instance.can_handle(url):
        return toutiao_plugin_instance
    return None
