import argparse
import sys
import time

from playwright.sync_api import sync_playwright

# 通用请求头
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
}


def fetch_normal(target_url: str) -> str:
    """普通模式：使用 stealth 插件，等待 networkidle"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=REQUEST_HEADERS["User-Agent"],
            java_script_enabled=True,
            extra_http_headers=REQUEST_HEADERS,
        )

        # 注入 stealth 插件以绕过简单的反爬
        try:
            context.add_init_script(path="src/omni_article_markdown/libs/stealth.min.js")
        except Exception as e:
            print(f"Warning: Could not load stealth.min.js. Error: {e}", file=sys.stderr)

        page = context.new_page()

        try:
            print(f"Fetching (Normal Mode): {target_url}", file=sys.stderr)
            page.goto(target_url, wait_until="networkidle", timeout=60000)
            html = page.content()
        except Exception as e:
            print(f"Error fetching page: {e}", file=sys.stderr)
            html = ""
        finally:
            page.close()
            context.close()
            browser.close()

    return html


def fetch_with_scroll(target_url: str) -> str:
    """滚动模式：增加等待时间并模拟滚动，适用于需要懒加载的页面 (如 Twitter/X)"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
            ],
        )
        context = browser.new_context(
            user_agent=REQUEST_HEADERS["User-Agent"],
            java_script_enabled=True,
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        try:
            print(f"Fetching (Scroll Mode): {target_url}", file=sys.stderr)
            # 对于需要滚动的页面，domcontentloaded 更合适，然后手动等待
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)

            # 等待页面初始资源加载
            print("Waiting for initial page load (15s)...", file=sys.stderr)
            time.sleep(15)

            # 尝试滚动页面以触发懒加载
            print("Scrolling to bottom...", file=sys.stderr)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)

            print("Scrolling back to top...", file=sys.stderr)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)

            html = page.content()
        except Exception as e:
            print(f"Error fetching page: {e}", file=sys.stderr)
            html = ""
        finally:
            page.close()
            context.close()
            browser.close()

    return html


def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="Fetch HTML content from a URL using Playwright.")
    parser.add_argument("url", help="The target URL to fetch.")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["normal", "scroll"],
        default="normal",
        help="The fetching mode to use. 'normal' waits for network idle. 'scroll' waits and scrolls to trigger lazy loading.",
    )

    args = parser.parse_args()

    target_url = args.url
    mode = args.mode

    if mode == "scroll":
        html_content = fetch_with_scroll(target_url)
    else:
        html_content = fetch_normal(target_url)

    # 将获取到的 HTML 打印到标准输出
    if html_content:
        print(html_content)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
