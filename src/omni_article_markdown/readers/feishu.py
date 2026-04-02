from typing import override

from ..launch_playwright import create_stealth_page
from ..reader import Reader
from ..utils import clean_text


class FeishuReader(Reader):
    """
    飞书文档使用虚拟列表，仅渲染可见内容，导致使用标准的 `page.content()` 无法完整捕获数据

    利用 Playwright 模拟用户滚动，动态触发内容加载，并通过 JS 注入收集所有已加载的内容区块，直到页面底部

    以下为尝试过的无效滚动方案：
    - page.mouse.wheel(delta_x=0, delta_y=800)
    - page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    - page.keyboard.press("End")
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def read(self) -> str:
        with create_stealth_page(self.reporter, self.verify_ssl) as (page, context):
            try:
                page.goto(self.url_or_path, wait_until="domcontentloaded", timeout=45000)
                js_function = """
                () => {
                    return document.title.trim().endsWith(" - 飞书云文档");
                }
                """
                page.wait_for_function(js_function, timeout=8000)

                # 调试用
                # return clean_text(page.content())

                self.report("开始动态滚动并收集内容区块...")

                collected_blocks: dict[str, str] = {}
                consecutive_no_new_blocks = 0
                max_retries = 5
                last_block_id = 0
                while consecutive_no_new_blocks < max_retries:
                    # --- 第一步：收集当前视口内的所有可见 Block ---
                    current_blocks = page.evaluate("""() => {
                        // 获取页面上所有的 block 元素
                        const allBlocks = Array.from(document.querySelectorAll('[data-block-id]'));

                        return allBlocks.filter(el => {
                            // 排除自身就是 page 根容器的情况
                            if (el.getAttribute('data-block-type') === 'page') return false;

                            // 检查当前 block 的父级链中，是否还有其他的 [data-block-id]
                            let parent = el.parentElement;
                            let isNested = false;

                            while (parent) {
                                // 如果向上找的过程中，发现父级也有 data-block-id，并且父级不是 'page'
                                if (parent.hasAttribute('data-block-id') && parent.getAttribute('data-block-type') !== 'page') {
                                    isNested = true; // 它是被别人嵌套的子块
                                    break;
                                }
                                parent = parent.parentElement;
                            }

                            // 只有不是被嵌套的“顶层块”才会被保留
                            return !isNested;

                        }).map(el => ({
                            id: el.getAttribute('data-block-id'),
                            type: el.getAttribute('data-block-type'),
                            html: el.outerHTML
                        }));
                    }""")

                    new_blocks_found = False
                    if current_blocks:
                        for b in current_blocks:
                            b_id = b["id"]
                            if b_id and b_id not in collected_blocks:
                                collected_blocks[b_id] = b["html"]
                                new_blocks_found = True

                    # --- 第二步：判定是否发现了新内容 ---
                    if new_blocks_found:
                        consecutive_no_new_blocks = 0
                        self.report(f"已收集 {len(collected_blocks)} 个内容块...")
                    else:
                        consecutive_no_new_blocks += 1
                        self.report(f"未发现新内容，正在等待加载 (尝试 {consecutive_no_new_blocks}/{max_retries})...")

                    last_block_id = page.evaluate("""() => {
                        const allBlocks = Array.from(document.querySelectorAll('[data-block-id]'));
                        // 过滤掉 'page' 根节点
                        const validBlocks = allBlocks.filter(el => el.getAttribute('data-block-type') !== 'page');

                        if (validBlocks.length === 0) return null;

                        // 按元素在页面中的 垂直位置 从 上 → 下 排序
                        validBlocks.sort((a, b) => {
                            return a.getBoundingClientRect().top - b.getBoundingClientRect().top;
                        });

                        // 返回 DOM 树中最后一个可见块的 ID，这是最接近底部的元素
                        return validBlocks[validBlocks.length - 1].getAttribute('data-block-id');
                    }""")

                    # page.evaluate(f"document.querySelector('[data-block-id=\"{last_block_id}\"]').scrollIntoView()")
                    page.evaluate(
                        f"""() => {{
                            const el = document.querySelector('[data-block-id="{last_block_id}"]');
                            if (el) el.scrollIntoView({{ block: "end", behavior: "instant" }});
                        }}"""
                    )

                    # 给予网络请求和 DOM 渲染充分的喘息时间
                    page.wait_for_timeout(500)

                self.report(f"飞书文档抓取完毕，共重组了 {len(collected_blocks)} 个内容区块。")

                # 获取真实的文档标题
                doc_title = clean_text(page.title())

                # 按照收集到的顺序拼接 HTML
                combined_html = f"""
                <html>
                <head><title>{doc_title}</title></head>
                <body>
                    <div class="page-block-children">
                        {"".join(collected_blocks.values())}
                    </div>
                </body>
                </html>
                """

                return clean_text(combined_html)
            except Exception as e:
                raise Exception(f"页面加载失败: {str(e)}")

    @override
    def can_handle(self) -> bool:
        return ".feishu.cn/" in self.url_or_path
