from importlib import resources
from typing import override

from ..launch_playwright import ensure_playwright_installed, try_launch_browser
from ..reader import USER_AGENT, Reader


class ScrollableBrowserReader(Reader):
    @override
    def read(self) -> str:
        playwright_context_manager = ensure_playwright_installed(self.reporter)
        with playwright_context_manager() as p:
            browser = try_launch_browser(p, reporter=self.reporter)
            context = browser.new_context(
                user_agent=USER_AGENT,
                java_script_enabled=True,
            )
            with resources.path("omni_article_markdown.libs", "stealth.min.js") as js_path:
                context.add_init_script(path=str(js_path))
            page = context.new_page()

            import time
            try:
                page.goto(self.url_or_path, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_selector('[data-testid="tweet"], article', timeout=30000)
                # 滚动页面以触发懒加载
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(5)
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(3)
            except Exception as e:
                self.report(f"页面加载提示: {str(e)}")

            html = page.content()

            # 优雅退出
            page.close()
            context.close()
            browser.close()

            return html

    @override
    def can_handle(self) -> bool:
        return "x.com" in self.url_or_path
