from typing import override

from ..extractor import Extractor, TagPredicate
from ..utils import filter_tag, is_matched_canonical


class SkillHubExtractor(Extractor):
    """
    SkillHub (skillhub.cn) 技能详情页

    结构要点：
    - 正文是「概述」Tab 里 div.markdown-body 渲染的 Markdown，由前端拉取后才出现，
      因此需要配合 BrowserReader 等待该选择器
    - 页面标题是 "文颜 - SkillHub"，正文首个 h1 是真实标题（wenyan-cli 发布指南），
      保留一个标题即可，故用 <title> 去后缀并删除正文 h1
    - 评分、安全报告、安装提示、相关推荐等都在 markdown-body 之外，收窄容器即排除
    """

    def __init__(self, soup):
        super().__init__(soup)
        # 基类 extract() 先跑 pre_handle_soup() 再取标题，正文 h1 会被提前删除，
        # 因此这里先把它缓存下来
        self._body_title: str = ""

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://skillhub.cn/skills/", self.soup) and bool(
            self.soup.find("div", class_="markdown-body")
        )

    @override
    def article_container(self) -> tuple:
        return ("div", {"class": "markdown-body"})

    @override
    def extract_title(self) -> str:
        # 正文首个 h1 是真正的文章标题（如「wenyan-cli 发布指南」），优先取它；
        # <title> 里的「文颜」只是技能名，信息量不足
        if self._body_title:
            return self._body_title
        title = super().extract_title()
        return title.removesuffix(" - SkillHub").strip() if title.endswith(" - SkillHub") else title

    @override
    def extract_description(self) -> str:
        # 概述正文已包含描述信息，再生成摘要会重复
        return ""

    @override
    def get_attrs_to_clean(self) -> list[TagPredicate]:
        return super().get_attrs_to_clean() + [
            # 表格里的脚注标记（如「否¹」「否²」）用 sup 渲染，保留会影响表格可读性
            lambda el: el.name == "button" and "copy" in " ".join(el.attrs.get("class", [])),
        ]

    @override
    def pre_handle_soup(self):
        body = filter_tag(self.soup.find("div", class_="markdown-body"))
        if not body:
            return
        # 正文 h1 作为文章标题：先缓存文本，再从正文移除，避免标题出现两次
        first_h1 = filter_tag(body.find("h1"))
        if first_h1:
            self._body_title = first_h1.get_text(strip=True)
            first_h1.decompose()
