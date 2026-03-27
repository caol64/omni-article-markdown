import sys

from playwright.sync_api import sync_playwright

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
}


def print_js_triggered_requests(target_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 建议开启 har 记录，如果需要离线分析详细堆栈
        context = browser.new_context(
            user_agent=REQUEST_HEADERS["User-Agent"],
            java_script_enabled=True,
            extra_http_headers=REQUEST_HEADERS,
        )
        context.add_init_script(path="src/omni_article_markdown/libs/stealth.min.js")
        page = context.new_page()

        def on_request(request):
            # 1. 过滤逻辑：通过 resource_type 锁定 JS 异步请求
            # 类型包括：xhr, fetch, websocket, eventsource
            if request.resource_type in ["fetch", "xhr"]:
                print("\n" + "=" * 80)
                print(f"🚀 [JS 异步请求] {request.method} | {request.resource_type}")
                print(f"🔗 URL: {request.url}")

                # # 2. 获取请求头
                # headers = request.headers
                # print(f"📂 Headers: {json.dumps(headers, indent=2, ensure_ascii=False)}")

                # # 3. 处理 POST 数据
                # if request.method == "POST" and request.post_data:
                #     print(f"📝 Post Data: {request.post_data}")

        # 监听请求
        page.on("request", on_request)

        # 访问页面
        page.goto(target_url, wait_until="domcontentloaded")

        # 关键：给异步请求留出时间
        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    # 简单的参数检查
    if len(sys.argv) < 2:
        print("Usage: uv run python fetch_url_playwright.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    print_js_triggered_requests(url)
