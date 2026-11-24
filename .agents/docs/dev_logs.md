# 开发踩坑日志（Agent 长期记忆）

> **唯一**的开发记录入口，取代已删除的 `agents/logs.md`，不要再新建同类日志文件。
> 用途：① 可泛化的教训 ② 站点不可抓取的原因（WAF/登录墙/截断）。

## 使用方式

- **开发前**：按关键词搜索（`truncate`、`BrowserReader`、`click`、公式、`og:title` …）。
- **开发后**：踩到**换站点/模块仍会复现**的坑才追加，用下方格式，**每条 ≤6 行**。
- 一次性事实（某站点今天的选择器）写进 extractor 代码注释，**不要**建条目。

### 条目格式

```markdown
## [LOG-YYYYMMDD-NNN] 一句话标题
- **现象**：（一句话）
- **根因**：（一句话，写清机制）
- **做法**：（可执行的规则，不是叙述）
- **验证**：（怎么确认修好了）
```

---

## [LOG-20261124-006] 公式：HTML 实体会残留进 `$…$`，命令尾空格令 Obsidian 渲染异常
- **现象**：`\(B &lt; B^*\)` → `$B &lt; B^*$`；`\(\sim \)125` → `$\sim $125`。
- **根因**：`_process_children()` 对所有文本节点转义 `<`→`&lt;`，而 MathJax 的 `\(…\)` 内容正是文本节点，转义后从未还原；源站 LaTeX 命令后确实带空格。
- **做法**：`normalize_tex()` 统一处理 ① 还原 `&lt; &gt; &amp;` ② 删公式**末尾**多余空格（`(?!\S)` 限定）③ 保留两类空格：`_TEX_SPACED_COMMANDS`（`\text{}`/`\begin{}` 等参数分隔）+ 命令后仍有内容的语义空格（`\sim 2B` ≠ `\sim2B`）。`$$…$$` 也是源站直出，需单独加 handler。
- **坑中坑**：`el.attrs.get("alt")` 是 **str 不是 list**，`" ".join(alt)` 会逐字符拆开导致匹配失败——判断图片 alt 一律用 `get_attr_text()`。
- **验证**：`pytest -k normalize_tex`；页面应出现 `$\sim$125`、`$B < B^*$`、`$C < \sum _e w_e$`。

## [LOG-20261124-005] 显式 `Accept-Language` 触发反爬，Playwright ctx 别乱加 header
- **现象**：百家号 `wait_for_selector("body")` 超时，日志 `locator resolved to hidden <body>`。
- **根因**：`create_stealth_page()` 把含 `Accept-Language` 的 `REQUEST_HEADERS` 塞进 `extra_http_headers`；覆盖该头被判异常，返回「百度安全验证」页（`body` 高度 0）。
- **做法**：浏览器上下文用独立的 `BROWSER_HEADERS`（只有 UA+Accept）；判断"是否被拦"先看 `page.title()` 与 `body.getBoundingClientRect().height`，再对 ctx 参数二分。
- **验证**：`span.bjh-p` 应为 17；`page.title()` 是文章标题而非验证页。

## [LOG-20261124-004] og:title 普遍带站名后缀，`extract_title()` 默认优先取 h1
- **现象**：标题输出成 `… | NVIDIA Technical Blog`、`… - Artificial Intelligence Review`。
- **根因**：`og:title` 被站点拼接品牌后缀。
- **做法**：新 extractor **默认重写 `extract_title()` 取页面 `<h1>`**，再 `return super().extract_title()` 兜底。例外：h1 是栏目名而非文章名时（yuzhi `themes` 页），改取正文容器内 h1。
- **验证**：看输出首行**和** `-s` 保存的文件名（文件名由 `to_snake_case(title)` 生成）。

## [LOG-20261124-003] 学术论文站：容器旁还有参考文献/附录，收窄会误删正文
- **现象**：SpringerLink 用 `div.main-content` 当容器输出干净，但 References/Appendices/Data availability/Funding 全消失。
- **根因**：这些是 `main-content` 的**兄弟节点**，同属 `div.c-article-body`；论文正文不在单一连续区块。
- **做法**：容器取外层 `c-article-body`，用谓词精确剔除 `c-article-recommendations` / `app-explore-related-subjects` / `#researcher-profile-container`。**不要**清「About this article」——`Cite this article`/`Keywords`/日期/DOI 是正式元数据。
- **验证**：改动前后**标题集合 diff**，应只少噪音标题（比看字节数可靠）。

## [LOG-20261124-002] `<video>` / `<audio>` 内容被静默丢弃
- **现象**：演示视频完全不出现。
- **根因**：两标签不在 `INLINE_ELEMENTS`/`BLOCK_ELEMENTS`，`case _` 只处理子节点文本，`<source src>` 无处输出。
- **做法**：加 `video|audio` 分支，取 `src`（或首个 `<source>`）输出 `[video](绝对URL)`，并把两标签加入 `BLOCK_ELEMENTS`；相对路径须 `urljoin`。
- **验证**：`<p><video><source src="/v/a.mp4"/></video></p>` 应得 `[video](https://x/v/a.mp4)`。

## [LOG-20261124-001] 图片与后续元素黏行：块级元素的 LB 被"折叠"吃掉
- **现象**：`![](4.gif)[上一篇…]` 黏在同一行。
- **根因**：`POST_HANDLERS` 第一步把**相邻多个 `LB_SYMBOL` 折叠成一个**。`<p><img></p>` 中 `img` 自带 LB、`p` 外层也有 LB，折叠后净丢一个分隔；紧跟的容器若不在 `BLOCK_ELEMENTS`（如 `nav`）又不加 LB。
- **做法**：`BLOCK_ELEMENTS` 必须覆盖所有语义块级标签——已补 `nav aside main header footer figure article details summary dl dt dd address`。
- **验证**：`<div><p><img/></p><nav>x</nav></div>` 应输出 `![A](…)\n\nx`；再跑多站点回归确认字节数不变。

## [LOG-20261123-003] "200 + 空容器"可能是页面不存在，不是渲染问题
- **现象**：`/docs/.../overview` 报 `Failed to extract article content.`，一度怀疑需要 Playwright。
- **根因**：该文档不存在，服务端仍返回 200 的空容器占位页；Playwright 抓到的碎片是渲染残留。
- **做法**：先比对同域一个确实存在的文档 URL 是否正常。当前实现"无正文→明确报错"是**正确**行为，不要为"不报错"加特殊回退。
- **验证**：`curl -I` 状态码 + 对照存在页面的正文长度。

## [LOG-20261123-002] 误判"必须用 Playwright"，白写了一套 reader 改动
- **现象**：给站点加 extractor 后失败，怀疑正文是前端注入，于是改 `BrowserReader` 加 `WAIT_FOR_CONTENT`。
- **根因**：**误判**。纯 `requests` 拿到的 HTML 里容器已有 3618 字正文。
- **做法**：判断"是否需要浏览器"必须实测一次——`requests.get` 后用 BeautifulSoup 取目标容器 `get_text(strip=True)`，非 0 就**不要**加 Playwright。Reader 选择应打印为 `HtmlReader`。
- **验证**：`ReaderFactory.create(url)` 返回的类名。

## [LOG-20261123-001] "加 extractor 反而报错"时，先查工厂命中与容器选择
- **现象**：加 extractor（容器 `#doc-viewer-container`）后报 `Failed to extract article content.`，而不写 extractor 走 `DefaultExtractor` 反而正常。
- **根因（已验证部分）**：`Extractor.extract()` 会遍历容器**全部子孙**套用 `ATTRS_TO_CLEAN`（含 `aria-hidden="true"`，该页有 15 个），"能提出多少正文"与预期偏差大。**具体是哪一版代码触发失败已无法复现**，不要臆断。
- **做法**：先用 `ExtractorFactory.create(soup)` 打印**实际选中的类名**，区分"没命中"与"命中但提取失败"；再用同一 soup 分别跑 `DefaultExtractor` 与自定义 extractor 对比字节数/首行/噪音词；**确认 SSR 无正文前不要动 reader**。
- **验证**：自定义 `Extractor` 子类跑 `extract()`，看返回 `None` 还是 `Article`。

## [LOG-20261119-002] Playwright 的 `[class="x"]` 是精确整串匹配
- **现象**：`wait_for_selector('div[class="editor"]')` 恒超时，即便元素存在且可见。
- **根因**：把 `[class="editor"]` 当属性值**完全相等**比较，而实际是 `"editor heti"`；`state="attached"` 也救不了。
- **做法**：`TARGET_HOSTS` 用 `div.editor` 或 `div[class~="editor"]`。**注意**仓库既有的 `main[class="main"]` 等写法依赖"class 恰好一个词"，属潜在脆弱点。
- **验证**：空白页 `set_content('<div class="foo bar">')` 后试三种选择器。

## [LOG-20261119-001] click 8.3 破坏了"裸 flag 带默认值"写法
- **现象**：`mdcli <url> -s` 裸用报 `Option '-s' requires an argument.`，8.2.1 正常。
- **根因**：click 8.3 把 `_flag_needs_value` 推导从"看 `flag_value`"改为"看 `default is UNSET`"，显式 `default=None` 时不再触发。
- **做法**：可选值选项统一用 `cli.py::_optional_value_option()`（显式置位 `_flag_needs_value=True`），**别手写 `flag_value`**。
- **验证**：裸写 `-s`、带值 `-s /path`、省略三种形态都要测。

## [LOG-20261119-003] 截断器遇开头巨型块会切出近空白
- **现象**：`--truncate 200` 只输出标题 + `…[truncated]`。
- **根因**：第一个正文块是 752 字符徽章墙（214 token），单块超预算，旧逻辑"超限即 break"。
- **做法**：截断时若**已用预算不足一半**，对当前块 `_hard_cut` 补足；正常段落序列仍保持块对齐。
- **验证**：测 200/300/600/800 四档，输出 token 应与预算同量级。

## [LOG-20261117-001] token 单系数估算两头不讨好
- **现象**：`utf8_bytes/2.5` 对纯英文高估约 30%。
- **根因**：单一系数无法同时适配 CJK(≈2.2 字节/token) 与拉丁(≈3.5–4)。
- **做法**：按 Unicode 区间分段折算（`_CJK_RE` + 两系数）；**非空文本必须保底 1 token**，否则 `int()` 抹零会让调用方死循环。
- **验证**：英文/中文/代码块/URL 密集四类样本偏差应落在 ±15%。

## [LOG-20261116-001] 排查站点失效：先判"没命中"还是"命中但失败"
- **现象**：A 类报 `Failed to extract article content.`（容器消失）；B 类不报错但输出全是导航（无 extractor 命中，落到 `DefaultExtractor`）。
- **根因**：两种失效形态表现不同，处理方向相反。
- **做法**：① `mdcli read <url>` 确认目标选择器是否还在；② `ExtractorFactory.create(soup)` 打印实际类名，立刻区分 A/B；③ 只有确认 SSR 无正文才考虑 reader。
- **验证**：按上述三步定位后再改代码。

## [LOG-20261111-001] 站点改版：保留旧模板兼容，别直接替换
- **现象**：oschina 改版后旧选择器全失效。
- **根因**：只支持单一模板，改版即失效。
- **做法**：`article_container()` 返回**列表**（新 → 旧 → 兜底），交给基类顺序尝试；`can_handle()` 同时接受新旧站名后缀。Cloudflare 同理用 `[新, 旧, main]` 三档。
- **验证**：用合成的旧模板 HTML 跑回归。

## [LOG-20261111-002] 标题污染会连锁污染文件名
- **现象**：标题输出成 `计费说明--向量数据库VikingDB-火山引擎`。
- **根因**：默认走 `og:title`（含站名），而 `save()` 用 `to_snake_case(title)` 生成文件名。
- **做法**：见 LOG-20261124-004——重写 `extract_title()` 优先取真实标题元素。
- **验证**：同时检查 Markdown 首行**和**保存后的文件名。

## [LOG-20261111-003] 照抄既有写法 ≠ 成立，每处都要最小验证
- **现象**：多次"按计划照抄仓库既有写法 → 实测直接报错"（click flag / Playwright 选择器 / SSR 误判）。
- **根因**：既有模式未必在当前依赖版本或当前 DOM 下成立。
- **做法**：每处"照抄"配一次 10 行内的最小验证；计划里的"预期输出"实施后逐条对照，不符就当场改计划。
- **验证**：验收标准逐条打勾。

## [LOG-20260513-001] WAF 站点必须用 Playwright，匹配特征别绑 URL
- **现象**：huxiu.com 用纯 `requests` 拿不到正文（阿里云 WAF）。
- **根因**：站点按 UA/JS 执行能力判定。
- **做法**：`BrowserReader.TARGET_HOSTS` 加域名前缀；`can_handle()` 用 `get_og_site_name()` 等元数据而非 URL 片段；标题取 `h1.article__title`（og:title 是 SEO 变体）。
- **验证**：`ReaderFactory.create(url)` 返回 `BrowserReader`；首尾段落完整。

## [LOG-20260410-001] 无 canonical 的站点：用 og:title 后缀做匹配
- **现象**：`developers.googleblog.com` 无稳定 canonical，`is_matched_canonical()` 无法命中。
- **根因**：canonical 缺失或指向根域。
- **做法**：`can_handle()` 改用 `get_og_title(soup).endswith("- Google Developers Blog")`；清理谓词按版式成组覆盖 `tags-/summary-/author-/social-/navigation-/related-posts-`。
- **验证**：`ExtractorFactory.create(soup)` 应返回目标类。

## 历史任务归档（原 `agents/logs.md`）

| 编号 | 日期 | 主题 | 说明 |
| --- | --- | --- | --- |
| LOG-20260513-001 | 2026-05-13 | HuxiuExtractor | 已提炼为同名教训条目 |
| LOG-20260410-001 | 2026-04-10 | GoogleBlogExtractor | 已提炼；原文声称新增的 `tests/test_googleblog_extractor.py` 实际不存在 |
| LOG-20260413-001 | 2026-04-13 | 新增 copilot-instructions.md | 纯流程记录，无技术价值 |