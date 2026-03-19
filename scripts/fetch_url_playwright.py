import sys

from playwright.sync_api import sync_playwright

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def fetch(target_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=REQUEST_HEADERS["User-Agent"],
            java_script_enabled=True,
            extra_http_headers=REQUEST_HEADERS,
        )
        context.add_init_script(path="src/omni_article_markdown/libs/stealth.min.js")
        page = context.new_page()
        page.goto(target_url, wait_until="networkidle")
        html = page.content()
        page.close()
        context.close()
        browser.close()
    return html


if __name__ == "__main__":
    # 简单的参数检查
    if len(sys.argv) < 2:
        print("Usage: uv run python fetch_url_playwright.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    html_content = fetch(url)
    print(html_content)
