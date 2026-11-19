import re

_FENCE_CODE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,}).*?^ {0,3}\1\s*$", re.MULTILINE | re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\r\n]+`")
_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n.*?\r?\n(?:---|\.\.\.)[ \t]*(?:\r?\n|\Z)", re.DOTALL)

# Markdown 结构信号
_SIGNALS = [
    re.compile(r"^ {0,3}#{1,6}[ \t]+\S", re.MULTILINE),  # ATX 标题
    re.compile(r"^ {0,3}(?:`{3,}|~{3,})", re.MULTILINE),  # 围栏代码块
    re.compile(r"!?\[[^\]]+\]\([^)\s]+\)"),  # 链接 / 图片
    re.compile(r"^\s*(?:[-*+]|\d+\.)[ \t]+\S", re.MULTILINE),  # 列表项
    re.compile(
        r"^\s*(?:\|\s*:?-{1,}:?\s*\||\|?\s*:?-{1,}:?(?:\s*\|\s*:?-{1,}:?)+\s*\|?)\s*$",
        re.MULTILINE,
    ),  # 表格分隔行（无 ReDoS）
    re.compile(r"^ {0,3}>[ \t]+\S", re.MULTILINE),  # 引用
]

_HTML_MARKERS = re.compile(r"<(?:!doctype|html|body)\b", re.IGNORECASE)
# 仅匹配合法 HTML 标签形态，排除换行与 <https://...> 自动链接
_TAG_RE = re.compile(r"</?[a-zA-Z][a-zA-Z0-9-]*(?:\s+[^>\r\n]*)?/?>")

_ATX_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)(?:[ \t]+#+)?\s*$")
_FALLBACK_MARKED_RE = re.compile(r"^(?:>[ \t]*|[-*+][ \t]+|\d+\.[ \t]+)(.+)$")
_LINK_OR_IMG_RE = re.compile(r"!?\[([^\]]*)\]\([^)\s]+\)")


def _clean_inline_markdown(text: str) -> str:
    text = _LINK_OR_IMG_RE.sub(r"\1", text)
    text = re.sub(r"\*\*|__|~~|`+", "", text)
    return text.strip()


def _strip_frontmatter_and_iter_non_code_lines(text: str):
    """跳过开头的 YAML Frontmatter 和围栏代码块，逐行产出原始行。"""
    cleaned = _FRONTMATTER_RE.sub("", text, count=1)
    fence_char = None
    fence_len = 0

    for line in cleaned.splitlines():
        fence_match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence_char is None:
            if fence_match:
                fence_char = fence_match.group(1)[0]
                fence_len = len(fence_match.group(1))
                continue
            yield line
        else:
            if re.match(rf"^ {{0,3}}{re.escape(fence_char)}{{{fence_len},}}\s*$", line):
                fence_char = None
                fence_len = 0


def looks_like_markdown(text: str) -> bool:
    if not text or not text.strip():
        return False
    if _HTML_MARKERS.search(text):
        return False

    # 剥离代码块后再统计 HTML 标签密度，防止代码块中的 HTML 示例被误杀
    text_no_code = _FENCE_CODE_RE.sub("", text)
    text_no_code = _INLINE_CODE_RE.sub("", text_no_code)
    lines = [line for line in text_no_code.splitlines() if line.strip()]
    if lines:
        tag_count = len(_TAG_RE.findall(text_no_code))
        if tag_count / len(lines) > 0.15:
            return False

    hits = sum(1 for pattern in _SIGNALS if pattern.search(text))
    return hits >= 2


def extract_markdown_title(text: str) -> str:
    """
    从 Markdown 文本中提取标题：
    首个一级标题 > 首个其他级别标题 > 首行带标记内容（引用/列表/链接） > 空串。
    """
    non_code_lines = list(_strip_frontmatter_and_iter_non_code_lines(text))

    first_sub_heading = ""
    for line in non_code_lines:
        m = _ATX_HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            title = _clean_inline_markdown(m.group(2))
            if not title:
                continue
            if level == 1:
                return title
            if not first_sub_heading:
                first_sub_heading = title

    if first_sub_heading:
        return first_sub_heading

    for line in non_code_lines:
        stripped = line.strip()
        if not stripped:
            continue
        m = _FALLBACK_MARKED_RE.match(stripped)
        if m:
            return _clean_inline_markdown(m.group(1))
        if _LINK_OR_IMG_RE.match(stripped):
            return _clean_inline_markdown(stripped)
        return ""

    return ""
