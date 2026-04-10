---
name: "reader-developer"
description: "AI-ready skill to fetch complete HTML source code using various techniques, including browser automation and API sniffing."
---

# Reader 开发者技能：全量 HTML 探测器

作为 `reader_developer`，你的核心目标是**“不计代价地获取完整源码”**。

## 1. 任务流（Workflow）
1.  **分级测试**：
    * **Level 1 (轻量)**：`uv run python scripts/fetch_url.py <url>`。
    * **Level 2 (动态)**：`uv run python scripts/fetch_url_playwright.py <url>`。
    * **Level 3 (深层)**：`uv run python scripts/fetch_url_playwright.py <url> -m scroll`。
2.  **验证**：对比抓取结果。如果 Level 1 只有空壳，而 Level 2 有正文，则确认该站必须使用浏览器渲染。
3.  **嗅探**：如果所有方法都抓不到正文，运行 `uv run python scripts/log_js_request.py <url>` 寻找潜在的 API 接口。
4.  **编码**：在 `src/omni_article_markdown/readers` 下创建 Python 类。

## 2. 核心类模板

你可以根据复杂程度选择**“复用配置”**或**“独立开发”**：

### 方案 A：通用浏览器复用（只需配置）
如果目标网站只需简单的 JS 渲染即可工作，只需在 `BrowserReader` 的 `TARGET_HOSTS` 中添加域名。

### 方案 B：自定义 Reader（针对复杂交互或加密站）
```python
from typing import override

from ..launch_playwright import create_stealth_page
from ..reader import Reader

class CustomDynamicReader(Reader):
    """
    针对具有复杂加载逻辑（如：异步解密、深度滚动）网站的 Reader
    """

    @override
    def can_handle(self, url: str) -> bool:
        # 保持逻辑简单且唯一
        return "target-complex-site.com" in url

    @override
    def read(self, url: str) -> Optional[str]:
        # 1. 尝试使用 Playwright 模拟滚动抓取
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            try:
                page.goto(self.url_or_path, wait_until="domcontentloaded", timeout=45000)
                html = page.content()
                # 2. 完整性检查：验证标题和正文是否存在
                if not html or "<article" not in html:
                    self.log_error(f"抓取失败或内容截断: {url}")
                    return None
                    
                # 3. 这里的逻辑可以包含：处理 Cookie、点击“阅读全文”按钮等
                return html
            except Exception as e:
                raise Exception(f"页面加载失败: {str(e)}")
```

## 3. 开发禁令（停止触发器）

如果遇到以下情况，**必须立即终止**并在 `agents/logs.md` 记录原因，不要尝试暴力破解：

* **人机校验**：出现 Cloudflare 5s 盾、图形验证码。
* **权限限制**：出现 `Login to continue` 或 `403 Forbidden`。
* **物理障碍**：`Connection Refused` 或 `404 Not Found`。
* **内容截断**：正文只有前两段，后面跟着“打开 App 查看全文”。

## 4. 质量审查清单 (QA)

在提交 `Reader` 之前，你需要确认：
- [ ] **标题一致性**：抓取到的 `<title>` 或 `<h1>` 是否与目标网页一致？
- [ ] **内容完整性**：搜索网页末尾的关键字，确认是否抓到了最后一段？
- [ ] **性能平衡**：能用 `requests` 解决的绝不用 `playwright`，减少系统开销。
- [ ] **唯一性**：`can_handle` 不会误伤到其他类似的域名。
