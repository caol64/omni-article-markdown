import argparse
import sys

import requests

REQUEST_HEADERS = {
}

# 普通浏览器 User-Agent
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"

# Curl User-Agent
CURL_UA = "curl/8.7.1"


def fetch(target_url, use_curl_ua=False):
    headers = REQUEST_HEADERS.copy()
    ua = CURL_UA if use_curl_ua else BROWSER_UA
    headers.update({"User-Agent": ua})

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple CLI to fetch HTML content.")

    # 位置参数：目标 URL
    parser.add_argument("url", help="The URL to fetch")

    # 可选参数：--curl (布尔开关)
    parser.add_argument("--curl", action="store_true", help="Use curl/8.7.1 as User-Agent instead of a browser")

    args = parser.parse_args()

    # 执行抓取
    html = fetch(args.url, use_curl_ua=args.curl)
    print(html)
