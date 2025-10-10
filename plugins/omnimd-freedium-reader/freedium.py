from importlib import resources
import sys
from runpy import run_module
from typing import override

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Playwright, Browser

from omni_article_markdown.extractor import Extractor
from omni_article_markdown.hookspecs import ReaderPlugin, hookimpl
from omni_article_markdown.utils import REQUEST_HEADERS, filter_tag


class FreediumExtractor(Extractor):
    """
    freedium.cfd
    """

    @override
    def can_handle(self, soup: BeautifulSoup) -> bool:
        title_tag = soup.title
        title = title_tag.get_text(strip=True) if title_tag else None
        return title is not None and title.endswith(" - Freedium")

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "main-content"})

    @override
    def extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = filter_tag(soup.find("h1"))
        if not title_tag:
            return ""
        title = title_tag.get_text(strip=True)
        title_tag.decompose()
        return title

    @override
    def extract_description(self, soup: BeautifulSoup) -> str:
        description_tag = soup.find("h2")
        if description_tag:
            description = description_tag.text.strip()
            description_tag.decompose()
            return description
        return super().extract_description(soup)


class FreediumPlugin(ReaderPlugin):
    @override
    def can_handle(self, url: str) -> bool:
        return "freedium.cfd" in url

    @override
    def read(self, url: str) -> str:
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
                else:
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
            html = page.content()
            page.close()
            context.close()
            browser.close()
        return html

    @override
    def extractor(self) -> Extractor | None:
        return FreediumExtractor()


@hookimpl
def get_custom_reader(url: str) -> ReaderPlugin | None:
    plugin_instance = FreediumPlugin()
    if plugin_instance.can_handle(url):
        return plugin_instance
    return None
