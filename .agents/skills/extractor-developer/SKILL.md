---
name: "extractor-developer"
description: "AI-ready skill to transform chaotic HTML into pure Markdown material using pattern recognition and DOM structure analysis."
---

# Extractor 开发者技能：精准正文提取器

作为 `extractor_developer`，你的目标是利用模式识别和 DOM 结构分析，将混乱的 HTML 转化为纯净的 Markdown 素材。

## 1. 任务流（Workflow）
1.  **探测**：调用 `uv run mdcli read <url>` 观察原始 HTML 结构。
2.  **定位**：识别 `article_container`（容器）和 `tags/attrs_to_clean`（噪音）。
3.  **编码**：在 `src/omni_article_markdown/extractors` 下创建 Python 类。
4.  **闭环验证**：运行 `uv run mdcli <url>` 检查最终 Markdown 的纯净度。

## 2. 核心类模板

你可以直接基于以下代码结构进行扩展。假设我们要为一个名为 `TechBlog` 的网站编写提取器：

```python
from typing import override

from ..extractor import Extractor
from ..utils import is_matched_canonical

class TechBlogExtractor(Extractor):
    """
    专门用于处理 TechBlog (example.com) 的正文提取器
    """

    @override
    def can_handle(self, url: str, soup: BeautifulSoup) -> bool:
        # 特征提取：通过域名或特定的 meta 标签识别，utils.py 中有一些开箱即用的函数
        return is_matched_canonical("https://example.com", self.soup)

    @override
    def article_container(self) -> List[dict]:
        # 优先级从高到低，精准锁定正文区域，剔除 header/footer
        return ("div", {"class": "post_body"})

    @override
    def get_attrs_to_clean(self) -> List[dict]:
        # 关键：通过属性清理掉侧边栏、推荐位、广告位
        return super().get_attrs_to_clean() + [
            {"class": "sidebar-wrapper"},
            {"class": "social-share-buttons"},
            {"id": "comments-section"},
            {"class": "breadcrumb-nav"}
        ]

    @override
    def pre_handle_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        # 进阶处理：处理 lazy-load 图片
        for img in soup.find_all("img"):
            if img.get("data-src"):
                img["src"] = img["data-src"]
        
        # 处理非标准段落（例如用 div 模拟的段落）
        for span in soup.find_all("span", class_="text-paragraph"):
            span.name = "p"
            
        return soup

    @override
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        # 如果默认提取器失败，尝试抓取自定义标题
        h1 = soup.find("h1", class_="entry-title")
        return h1.get_text(strip=True) if h1 else None
```

## 3. 黄金原则（Extractor 黄金准则）

作为 `extractor_developer`，你在编写代码时应遵循以下“品味”：

* **容器优先**：优先配置 `article_container`。如果能定位到正文 `div`，你就已经赢了 80%，因为容器外的广告和导航会被物理切断。
* **语义化转换**：如果原始网页为了视觉效果把 `<h2>` 写成了 `<div class="big-title">`，请在 `pre_handle_soup` 中将其还原，这决定了 Markdown 的目录层级。
* **图片保真**：必须检查 `data-src`、`original-src` 等属性，确保抓取到的不是 1x1 的占位图。
* **噪音最小化**：清理掉 `button`、`input`、`form`。正文不需要任何交互逻辑。这在`Extractor`父类中已经实现，无需特别处理。

## 4. 验证命令清单

```bash
# 第一步：查看原始内容（确认是否有 JS 加载或混淆）
uv run mdcli read https://example.com/article/1

# 第二步：编写并保存 extractor 到 src/omni_article_markdown/extractors/techblog_extractor.py

# 第三步：运行最终转换，检查终端输出的 Markdown 质量
uv run mdcli https://example.com/article/1
```

## 5. 禁止事项

- 在**探测**阶段，**禁止**使用`uv run mdcli read <url>`以外的方式获取 HTML 结构。
