import sys
from typing import override

from ..reader import Reader
from playwright.sync_api import Browser, Playwright, sync_playwright


TARGET_HOSTS = [
    "developer.apple.com/documentation/",
    "www.infoq.cn/",
    "pcsx2.net/",
    "baijiahao.baidu.com/",
    "www.snowflake.com/en/blog/",
]


class BrowserReader(Reader):
    @override
    def read(self) -> str:
        import time

        def try_launch_browser(p: Playwright) -> Browser:
            try:
                return p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-accelerated-2d-canvas",
                        "--disable-gpu",
                        "--window-size=1920,1080",
                    ],
                )
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
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                java_script_enabled=True,
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            # 对于 Twitter/X，使用 domcontentloaded 而不是 networkidle
            # 因为 Twitter 的连接可能永远不会 idle
            if "x.com" in url or "twitter.com" in url:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                # 等待推文内容加载
                try:
                    page.wait_for_selector('[data-testid="tweet"], article', timeout=30000)
                    # 滚动页面以触发懒加载
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(5)
                    page.evaluate("window.scrollTo(0, 0)")
                    time.sleep(3)
                except Exception:
                    pass  # 继续执行，即使等待超时
            else:
                page.goto(url, wait_until="networkidle")

            html = page.content()
            page.close()
            context.close()
            browser.close()
        return html

    @override
    def can_handle(self) -> bool:
        return any(self.url_or_path.startswith(host) for host in TARGET_HOSTS)
