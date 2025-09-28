import sys
import importlib
from typing import Optional

from bs4 import BeautifulSoup
from omni_article_markdown.extractor import Extractor
from omni_article_markdown.hookspecs import hookimpl, ReaderPlugin
from omni_article_markdown.utils import REQUEST_HEADERS
from playwright.sync_api import sync_playwright
from runpy import run_module


class FreediumExtractor(Extractor):
    """
    freedium.cfd
    """

    def can_handle(self, soup: BeautifulSoup) -> bool:
        title_tag = soup.title
        title = title_tag.text.strip() if title_tag else None
        return title and title.endswith(" - Freedium")

    def article_container(self) -> tuple:
        return ("div", {"class": "main-content"})

    def extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find("h1")
        title = title_tag.text.strip()
        title_tag.decompose()
        return title

    def extract_description(self, soup: BeautifulSoup) -> str:
        description_tag = soup.find("h2")
        if description_tag:
            description = description_tag.text.strip()
            description_tag.decompose()
            return description
        return super().extract_description(soup)



class FreediumPlugin(ReaderPlugin):
    def can_handle(self, url: str) -> bool:
        return "freedium.cfd" in url

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
            with importlib.resources.path("omni_article_markdown.libs", "stealth.min.js") as js_path:
                context.add_init_script(path=str(js_path))
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            html = page.content()
            page.close()
            context.close()
            browser.close()
        return html

    def extractor(self) -> Optional[Extractor]:
        return FreediumExtractor()


@hookimpl
def get_custom_reader(url: str) -> Optional[ReaderPlugin]:
    plugin_instance = FreediumPlugin()
    if plugin_instance.can_handle(url):
        return plugin_instance
    return None
