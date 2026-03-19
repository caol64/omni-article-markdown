import argparse
import sys

import requests

REQUEST_HEADERS = {
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

# 普通浏览器 User-Agent
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"

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
    parser.add_argument(
        "--curl",
        action="store_true",
        help="Use curl/8.7.1 as User-Agent instead of a browser"
    )

    args = parser.parse_args()

    # 执行抓取
    html = fetch(args.url, use_curl_ua=args.curl)
    print(html)
