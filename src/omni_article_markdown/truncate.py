from .utils import _CJK_BYTES_PER_TOKEN, count_tokens

DEFAULT_TOKEN_LIMIT = 800
TRUNCATE_MARK = "…[truncated]"


def truncate_markdown(text: str, max_tokens: int = DEFAULT_TOKEN_LIMIT) -> str:
    """
    将 Markdown 文本截断到约 max_tokens 个 token（count_tokens 分段近似）。

    - 以空行分隔的块为最小单位收尾，避免劈坏表格、图片语法；
    - 截断点若落在未闭合的代码围栏内，回退到该围栏起始块之前；
    - 发生截断时追加 “…[truncated]” 标记。
    """
    text = text.strip()
    if count_tokens(text) <= max_tokens:
        return text

    blocks = _split_blocks(text)
    kept: list[str] = []
    used = 0
    budget = max_tokens - count_tokens(TRUNCATE_MARK)

    for block in blocks:
        cost = count_tokens(block) + (2 if kept else 0)  # 块间 "\n\n" 的字节折算
        if used + cost > budget:
            break
        kept.append(block)
        used += cost

    # 代码围栏保护：结尾仍处于未闭合状态时，回退到围栏起始块之前
    while _ends_inside_fence(kept):
        kept.pop()

    # 极端情况：首块即超预算，按字节预算硬切并保证 UTF-8 字符边界完整
    if not kept:
        kept.append(_hard_cut(blocks[0], budget))

    result = "\n\n".join(kept).rstrip()
    return f"{result}\n\n{TRUNCATE_MARK}"


def _split_blocks(text: str) -> list[str]:
    """
    按空行切块，但代码围栏内部的空行不切分（围栏必须保持为单个块）。
    """
    blocks: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            current.append(line)
            continue
        if not in_fence and not line.strip():
            if current:
                blocks.append("\n".join(current))
                current = []
            continue
        current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def _ends_inside_fence(kept: list[str]) -> bool:
    fence_count = sum(1 for b in kept if b.lstrip().startswith("```"))
    return fence_count % 2 == 1


def _hard_cut(block: str, budget_tokens: int) -> str:
    """
    在 budget_tokens 近似预算内切断单个块，不产生半个多字节字符。
    以 count_tokens 为唯一计价口径：先按最紧系数（CJK）折算出字节上界截取，
    再逐步缩短直到估算值落入预算，保证与主循环的预算语义一致。
    """
    data = block.encode("utf-8")
    hi = min(len(data), max(1, int(budget_tokens * _CJK_BYTES_PER_TOKEN)))
    lo = 0
    best = ""
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = _decode_prefix(data[:mid])
        if candidate is None:
            hi = mid - 1
            continue
        if count_tokens(candidate) <= budget_tokens:
            best = candidate
            lo = mid + 1
        else:
            hi = mid - 1
    return best.rstrip()


def _decode_prefix(data: bytes) -> str | None:
    """回退到完整 UTF-8 字符边界后解码；失败返回 None。"""
    while data:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            data = data[:-1]
    return ""
