from typing import override

from bs4 import BeautifulSoup, Tag

from ..extractor import Extractor
from ..utils import filter_tag, is_matched_canonical


class VllmDocsExtractor(Extractor):
    """
    vLLM 文档 (docs.vllm.ai，Material for MkDocs 主题)

    结构要点：
    - 正文在 article.md-content__inner，侧栏目录在同级 aside，收窄容器即排除
    - <title> 是 "Speculative Decoding - vLLM"，与正文 <h1> 重复；
      保留一个标题即可，故用 <title> 去掉站点后缀，并删除正文首个 h1
    - 标题末尾带 Material 的 "¶" 锚点，需清除
    - 少量代码块被源站错误地写成 <p>```python ...</p>，需还原成 <pre>
    """

    @override
    def can_handle(self) -> bool:
        return is_matched_canonical("https://docs.vllm.ai/", self.soup) and bool(
            self.soup.find("article", class_="md-content__inner")
        )

    @override
    def article_container(self) -> tuple:
        return ("article", {"class": "md-content__inner"})

    @override
    def extract_title(self) -> str:
        # <title> 形如 "Speculative Decoding - vLLM"，去掉 " - vLLM" 后缀
        title = super().extract_title()
        return title.removesuffix(" - vLLM").strip() if title.endswith(" - vLLM") else title

    @override
    def get_attrs_to_clean(self) -> list:
        return super().get_attrs_to_clean() + [
            # 页脚「Source file / Last updated」时间戳
            lambda el: "class" in el.attrs and "md-source-file" in el.attrs["class"],
        ]

    @override
    def pre_handle_soup(self):
        body = filter_tag(self.soup.find("article", class_="md-content__inner"))
        if not body:
            return

        # 1) 去掉标题里的 ¶ 锚点（Material 主题的 permalink）
        for anchor in body.find_all("a", class_="headerlink"):
            anchor.decompose()
        for heading in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            if heading.get_text(strip=True).endswith("¶"):
                heading.string = heading.get_text(strip=True).removesuffix("¶").strip()

        # 2) 删除正文首个 h1：标题已由 <title> 提供，避免出现两个一级标题
        first_h1 = filter_tag(body.find("h1"))
        if first_h1:
            first_h1.decompose()

        # 3) 还原被错误包在 <p> 里的围栏代码块
        self._restore_fenced_code_blocks(body)

    def _restore_fenced_code_blocks(self, body: BeautifulSoup | Tag):
        # 先收集候选再处理：替换后原节点已脱离文档，边遍历边改会把后续段落重复处理
        candidates = [p for p in body.find_all("p") if p.get_text().lstrip().startswith("```")]
        for paragraph in candidates:
            code_text = self._collect_fence_text(paragraph)
            if not code_text:
                continue
            pre = self.soup.new_tag("pre")
            code = self.soup.new_tag("code")
            code.string = code_text
            pre.append(code)
            paragraph.replace_with(pre)
            # 其余同属该代码块的段落一并移除
            for consumed in self._consumed[1:]:
                consumed.decompose()

    def _collect_fence_text(self, start: Tag) -> str:
        """
        从起止 ``` 的段落开始向后收集，直到遇到结束的 ``` 段落；
        期间换行被 <br/> 拆成了同一段落里的多行，需要合并成一个 <pre>。
        """
        self._consumed: list[Tag] = []
        blocks: list[Tag] = []
        current: Tag | None = start
        while isinstance(current, Tag):
            blocks.append(current)
            if current is not start and current.get_text().strip().endswith("```"):
                break
            current = current.find_next_sibling()
        if not blocks:
            return ""
        self._consumed = blocks

        lines: list[str] = []
        for block in blocks:
            for line in self._paragraph_lines(block):
                lines.append(line)
        joined = "\n".join(lines).strip()
        # 去掉首尾围栏行
        if joined.startswith("```"):
            joined = joined.split("\n", 1)[1] if "\n" in joined else ""
        if joined.rstrip().endswith("```"):
            joined = joined.rstrip()[:-3]
        return joined.strip("\n")

    @staticmethod
    def _paragraph_lines(block: Tag) -> list[str]:
        raw = str(block)
        inner = raw[len("<p>") : -len("</p>")] if raw.startswith("<p>") else raw
        inner = inner.replace("<br/>", "\n").replace("<br>", "\n").replace("<br />", "\n")
        text = BeautifulSoup(inner, "html.parser").get_text()
        return text.split("\n")
