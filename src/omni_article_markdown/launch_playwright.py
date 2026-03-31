import subprocess
import sys
from collections.abc import Generator
from contextlib import contextmanager
from importlib import resources
from typing import Any

from .http_client import REQUEST_HEADERS, USER_AGENT
from .reporter import Reporter


def _install_package(package_name: str, reporter: Reporter | None = None):
    """使用独立进程安装 Python 依赖包 (如 playwright)"""
    if reporter:
        reporter(f"正在通过 pip 安装 {package_name}，请稍候...")

    cmd = [sys.executable, "-m", "pip", "install", package_name]

    try:
        # capture_output=False 允许 pip 的原生进度条显示在终端上
        subprocess.run(cmd, check=True, stdout=sys.stderr, stderr=sys.stderr)
        if reporter:
            reporter(f"{package_name} 安装成功!")
    except subprocess.CalledProcessError as e:
        if reporter:
            reporter(f"{package_name} 安装失败，退出码: {e.returncode}")
        raise Exception(f"无法安装必要的 Python 依赖包: {package_name}")


def _install_chromium_browser(reporter: Reporter | None = None):
    """专门负责安装 Playwright 依赖的 Chromium 浏览器内核"""
    if reporter:
        reporter("正在下载 Chromium 浏览器内核，这可能需要几分钟...")

    cmd = [sys.executable, "-m", "playwright", "install", "chromium-headless-shell"]

    try:
        subprocess.run(cmd, check=True, stdout=sys.stderr, stderr=sys.stderr)
        if reporter:
            reporter("Chromium 内核安装完成!")
    except subprocess.CalledProcessError as e:
        if reporter:
            reporter(f"Chromium 内核安装失败，退出码: {e.returncode}")
        raise Exception("无法安装 Playwright 内核")


def ensure_playwright_installed(reporter: Reporter | None = None):
    """
    环境检查探针。
    如果在未安装 playwright 的环境下被调用，会触发一整套的自动化环境搭建。
    安装成功后，将返回原生的 sync_playwright 上下文管理器供业务层使用。
    """
    try:
        # 1. 尝试局部导入 (只有在这里才会触发 ModuleNotFoundError)
        from playwright.sync_api import sync_playwright
    except (ImportError, ModuleNotFoundError):
        # 2. 如果包不存在，先通过 pip 安装 python 库
        if reporter:
            reporter("未检测到 playwright 库，正在为您自动配置高级抓取环境...")
        _install_package("playwright==1.57.0", reporter)

        # 重新尝试导入刚刚安装好的包
        from playwright.sync_api import sync_playwright

    # 返回上下文生成器给外部业务调用
    return sync_playwright


def try_launch_browser(p, reporter: Reporter | None = None):
    """
    接收传入的 playwright 对象，尝试启动浏览器。
    如果报缺少内核的错误，则自动安装并重试。

    这里的 p 类型是 playwright.sync_api.Playwright，但由于不能在文件顶部 import，
    我们在参数类型提示中去掉了严格校验，采用鸭子类型 (Duck Typing)。
    """
    try:
        # 首先尝试静默启动
        return p.chromium.launch(headless=True)
    except Exception as e:
        error_msg = str(e)

        # 捕获经典的内核缺失错误
        if "Executable doesn't exist" in error_msg or "playwright install" in error_msg:
            if reporter:
                reporter("Playwright 引擎已就绪，但缺失对应的浏览器内核。")

            # 触发内核下载
            _install_chromium_browser(reporter)

            # 再次尝试启动
            if reporter:
                reporter("环境配置完毕，正在启动无头浏览器...")
            return p.chromium.launch(headless=True)

        # 其他系统级错误直接抛出
        raise


@contextmanager
def create_stealth_page(reporter: Reporter | None = None, verify_ssl: bool = True) -> Generator[tuple[Any, Any]]:
    """
    提供一个开箱即用的、自带 Stealth 防爬插件的 Playwright Page 和 Context。
    使用 @contextmanager 确保在 yield 结束后，浏览器资源会被妥善关闭。
    """
    # 1. 确保环境安装
    playwright_context_manager = ensure_playwright_installed(reporter)

    # 2. 启动 Playwright
    with playwright_context_manager() as p:
        browser = try_launch_browser(p, reporter=reporter)

        # 3. 创建带有统一配置的 Context
        context = browser.new_context(
            user_agent=USER_AGENT,
            java_script_enabled=True,
            extra_http_headers=REQUEST_HEADERS,
            ignore_https_errors=not verify_ssl,  # 统一处理 SSL 验证
        )

        # 4. 注入 Stealth 插件
        try:
            with resources.path("omni_article_markdown.libs", "stealth.min.js") as js_path:
                context.add_init_script(path=str(js_path))
        except Exception as e:
            if reporter:
                reporter(f"无法加载 stealth 插件，将使用标准模式: {e}")

        page = context.new_page()

        try:
            # 将 page 和 context 作为元组 yield 出去，供业务代码在 with 块中使用
            # 返回 context 是因为有些业务（如知乎）需要调用 context.cookies()
            yield page, context

        finally:
            # 无论业务代码是否抛出异常，这里都会在 with 块结束时完美释放资源
            for obj in (page, context, browser):
                try:
                    if obj:
                        obj.close()
                except Exception:
                    pass
