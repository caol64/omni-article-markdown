from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import filter_tag, is_matched_canonical


class VolcengineDocsExtractor(Extractor):
    """
    火山引擎文档中心 (volcengine.com / docs.volcengine.com)

    说明：正文已由服务端渲染成 HTML，**不需要** Playwright，默认 HtmlReader 即可。
    选择器特征依据：
    - canonical 统一指向 www.volcengine.com/docs/（docs. 子域也跳这里）
    - 正文容器 #doc-viewer-container 的直系子节点是空的 div.volc-md-viewer，
      真实段落位于更深层嵌套中
    - 文档不存在时服务端仍返回 200 且容器为空（如 overview/quickstart），
      由基类“正文为空则报错”兜底
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://www.volcengine.com/docs/", self.soup) and bool(
            self.soup.find("div", id="doc-viewer-container")
        )

    @override
    def article_container(self) -> tuple:
        return ("div", {"id": "doc-viewer-container"})

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            # 页面顶部的“文档反馈 / 问问助手”浮层
            lambda el: "class" in el.attrs and "contentfeedback" in " ".join(el.attrs["class"]),
            # 自定义 block 的告警图标块
            lambda el: "class" in el.attrs and "volc-custom-block-warning" in el.attrs["class"],
        ]

    @override
    def extract_title(self) -> str:
        # 文档标题在文章容器之外（div.titleRow），<title> 带“--产品名-火山引擎”后缀
        row = filter_tag(self.soup.find("div", class_="titleRow-DONu"))
        if row:
            for child in row.find_all(recursive=False):
                text = child.get_text(strip=True)
                if text:
                    return text
        return super().extract_title()

    @override
    def pre_handle_soup(self):
        body = self.soup.find("div", id="doc-viewer-container")
        if not body:
            return
        # 站内标题用 div.md-h1~h4 渲染，还原为真实标题标签以获得 Markdown 大纲
        for class_name, tag_name in (("md-h1", "h2"), ("md-h2", "h3"), ("md-h3", "h4"), ("md-h4", "h5")):
            for heading in body.find_all("div", class_=class_name):
                heading.name = tag_name
        # 标题后的 “#” 锚点与外链箭头图标
        for anchor in body.find_all("a", class_="header-anchor"):
            anchor.decompose()
        for icon in body.find_all("svg"):
            icon.decompose()
