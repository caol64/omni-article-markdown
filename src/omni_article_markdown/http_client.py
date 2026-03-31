from functools import cache

import requests
import urllib3

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"


REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

@cache
def get_session(verify_ssl: bool = True) -> requests.Session:
    """
    获取全局复用的 requests.Session 单例。
    利用 @cache 装饰器，相同参数的调用将永远返回同一个 Session 实例，
    完美实现连接池共享和参数化单例。
    如果是长期运行的服务，建议定期调用 session.close() 来清理过期连接。
    """
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)
    session.verify = verify_ssl

    # 如果禁用了 SSL 验证，在此处统一屏蔽警告
    if not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    return session
