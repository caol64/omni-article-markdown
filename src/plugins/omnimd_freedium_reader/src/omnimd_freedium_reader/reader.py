import sys
import importlib
from typing import Optional
from omni_article_markdown.hookspecs import hookimpl, ReaderPlugin
from omni_article_markdown.utils import REQUEST_HEADERS
from playwright.sync_api import sync_playwright
from runpy import run_module


class FreediumReader(ReaderPlugin):
    def can_handle(self, url: str) -> bool:
        return "freedium.cfd" in url

    def read(self, url: str) -> str:
        # print(f"Using FreediumReader for: {url}")
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
            html = page.content()
            page.close()
            context.close()
            browser.close()
        return html



# 实例化插件
freedium_plugin_instance = FreediumReader()

@hookimpl
def get_custom_reader(url: str) -> Optional[ReaderPlugin]:
    if freedium_plugin_instance.can_handle(url):
        return freedium_plugin_instance
    return None
