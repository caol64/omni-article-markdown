import sys
from typing import Optional
from omni_article_markdown.hookspecs import hookimpl, ReaderPlugin
from omni_article_markdown.utils import REQUEST_HEADERS
from playwright.sync_api import sync_playwright
from runpy import run_module


class AppleDevelopReader(ReaderPlugin):
    def can_handle(self, url: str) -> bool:
        return "developer.apple.com/documentation/" in url

    def read(self, url: str) -> str:
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
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            html = page.content()
            page.close()
            context.close()
            browser.close()
        return html



# 实例化插件
appledev_plugin_instance = AppleDevelopReader()

@hookimpl
def get_custom_reader(url: str) -> Optional[ReaderPlugin]:
    if appledev_plugin_instance.can_handle(url):
        return appledev_plugin_instance
    return None
