# 开发踩坑日志（Agent 长期记忆）

> 本文件是**唯一**的开发记录入口，同时承担三种记录：
> 1. **教训条目**（主体）：已踩过并已修正、**可泛化**的坑；
> 2. **站点抓取档案**：站点不可抓取的原因（WAF/登录墙/截断），供后续判断"该不该再试"；
> 3. **历史任务归档**（文末）：早期 `agents/logs.md` 的任务流水，价值已提炼进教训条目。
>
> 本文件取代了已删除的 `agents/logs.md`，**不要再新建同类日志文件**。

## 使用方式

- **开发前**：搜索本文件中与你要改的模块相关的关键词（如 `truncate`、`BrowserReader`、`click`、`aria-hidden`）。
- **开发后**：若你踩到了一个**新的、可复用的坑**（换一个站点/模块仍会复现），按下方格式追加一节。
- **站点不可抓取时**：把人机校验/登录墙/内容截断等**终止原因**记入，这是后续判断"该不该再试"的依据。
- **不要**把一次性事实（某个站点今天的选择器）单独记成条目——那属于 extractor 代码注释或文末归档。

### 条目格式

```markdown
## [LOG-YYYYMMDD-NNN] 一句话标题

- **现象**：
- **根因**：
- **正确做法**：
- **验证方式**：
- **相关文件**：
```

---

## [LOG-20261123-001] "加 extractor 反而报错"时，先怀疑自己的容器选择，再怀疑 reader

- **现象**：给火山引擎文档加 extractor（容器 `#doc-viewer-container`）时报
  `Error: Failed to extract article content.`；但**不写** extractor、走 `DefaultExtractor` 反而正常输出。
- **当时的误判**：以为是"reader 拿到的容器是空的"，于是去改 `BrowserReader` 加 Playwright 配置。
  该判断**错误**，事后被证实（见 LOG-20261123-002）。
- **已验证的机制**：`Extractor.extract()` 会遍历容器**全部子孙**套用 `ATTRS_TO_CLEAN`
  （`display:none` / `hidden` / `aria-hidden="true"` / `katex-html`）。该页正文里有 **15 个**
  `aria-hidden="true"` 的子孙节点会被删除——这会让"容器里能提出多少正文"与"预期"产生明显偏差。
  当前 DOM 中容器**自身**没有 `aria-hidden`，所以容器不会被自删；**具体是哪一版代码触发失败已无法复现**，
  不做断言。
- **正确做法**：
  1. 先用 `ExtractorFactory.create(soup)` 打印**实际选中的 extractor 类名**——立刻区分
     "没命中"（落到 DefaultExtractor）与"命中了但提取失败"；
  2. 用同一个 soup 分别跑 `DefaultExtractor` 与自定义 extractor，比较字节数/首行/噪音词；
  3. **不要**在没确认 SSR 无正文之前动 reader（见 LOG-20261123-002）。
- **验证方式**：`uv run python -c` 里构造自定义 `Extractor` 子类跑 `extract()`，看返回 `None` 还是 `Article`。
- **相关文件**：`src/omni_article_markdown/extractor.py`（`extract()`、`ATTRS_TO_CLEAN`、`ExtractorFactory`）

---

## [LOG-20261123-002] 误判"必须用 Playwright"，结果白写了一套 reader 改动

- **现象**：火山引擎文档加 extractor 后失败，怀疑正文是前端注入的，于是给 `BrowserReader` 加了
  `TARGET_HOSTS` + `WAIT_FOR_CONTENT`（`networkidle` + 等待 `innerText` 非空）。
- **根因**：**误判**。实测纯 `requests` 拿到的 HTML 里 `#doc-viewer-container` 已有 3618 字正文，
  完全不需要 JS 渲染。失败的真实原因见 LOG-20261123-001。
- **正确做法**：判断"是否需要浏览器"时，用最低成本的方式验证一次：
  ```bash
  uv run python -c "
  import requests
  from bs4 import BeautifulSoup
  h = requests.get('<url>', headers={'User-Agent':'Mozilla/5.0'}, timeout=30).text
  b = BeautifulSoup(h,'html.parser').find('div', id='<你的容器id>')
  print(len(b.get_text(strip=True)) if b else 'no container')"
  ```
  非 0 就说明 SSR 已输出，**不要**加 Playwright。
- **验证方式**：Reader 选择应打印为 `HtmlReader` 而非 `BrowserReader`。
- **相关文件**：`src/omni_article_markdown/readers/browser.py`（最终已回退，未保留火山引擎配置）

---

## [LOG-20261123-003] 文档站对不存在的路径返回 200 + 空容器，会把"页面不存在"伪装成"解析失败"

- **现象**：`/docs/.../overview`、`/docs/.../quickstart` 报 `Failed to extract article content.`，
  一度以为需要 Playwright；Playwright 渲染出 854 字，更像是"页面存在但 SSR 缺失"。
- **根因**：这两个文档**根本不存在**。服务端返回 `200` 的"帮助文档"占位页，正文容器为空。
  Playwright 抓到的那点文字是渲染残留片段，不是真正文。
- **正确做法**：面对"200 但正文为空"，先用 HTTP 状态 + 正文特征双重判断，不要拿浏览器当万能钥匙。
  项目当前行为（无正文 → 明确报错）是**正确**的，不要为了"不报错"去加特殊回退。
- **验证方式**：对比同域一个确实存在的文档 URL（如 `billing-instructions`）是否正常。
- **相关文件**：`src/omni_article_markdown/omni_article_md.py`（`_extract_article` 的空正文守卫）

---

## [LOG-20261119-001] click 8.3 破坏了"裸 flag 带默认值"写法

- **现象**：`mdcli <url> -s`（不带路径）在 click 8.3.1 下报 `Option '-s' requires an argument.`，
  但帮助文本写着 "Use -s alone to save to './'"。同样写法在 8.2.1 正常。
- **根因**：click 8.3 把 `_flag_needs_value` 的推导从"看 `flag_value is not None`"改成
  "看 `default is UNSET`"；显式传了 `default=None` 时不再触发。
- **正确做法**：用 `cli.py` 里的 `_optional_value_option()` 装饰器封装——构造 `click.Option` 后
  显式置位 `opt._flag_needs_value = True`，兼容 8.2/8.3。**新增可选值选项时复用它，别手写。**
- **验证方式**：三种调用形态都要测：裸写 `-s`、带值 `-s /path`、省略。
- **相关文件**：`src/omni_article_markdown/cli.py`

---

## [LOG-20261119-002] Playwright 的 `[class="x"]` 是精确整串匹配

- **现象**：`page.wait_for_selector('div[class="editor"]')` 在 oschina 上必超时，即使元素存在且可见。
- **根因**：Playwright 把 `[class="editor"]` 当作属性值**完全相等**比较，而实际 class 是
  `"editor heti"`，因此永不匹配。`state="attached"` 也救不了。
- **正确做法**：`TARGET_HOSTS` 里的选择器用 `div.editor` 或 `div[class~="editor"]`（包含匹配）。
  **注意**：仓库里既有的 `main[class="main"]`、`div[class="article-content-wrap"]` 等写法都依赖
  "该元素 class 恰好只有一个词"才成立，属潜在脆弱点，改动它们前先实测。
- **验证方式**：空白页最小复现——`page.set_content('<div class="foo bar">')` 后分别试三种选择器。
- **相关文件**：`src/omni_article_markdown/readers/browser.py`

---

## [LOG-20261119-003] 截断器按"块"收尾时，遇到开头就是巨型块会把输出切成几乎空白

- **现象**：`mdcli <raw README.md> --truncate 200` 只输出标题 + `…[truncated]`，内容形似"空"。
- **根因**：该 README 第 2 个块是 752 字符的徽章墙（214 token），单块就超预算；旧逻辑
  "块是最小单位、超限即 break"，于是只剩前面的标题块。
- **正确做法**：截断时若**已用预算不足一半**，对当前块做硬切补足（`_hard_cut`），
  正常段落序列仍保持严格块对齐。改 `truncate.py` 后务必用"开头是巨型块"的样本回归。
- **验证方式**：分别测 200/300/600/800 四档，确认输出 token 数与预算同量级、且结尾有标记。
- **相关文件**：`src/omni_article_markdown/truncate.py`

---

## [LOG-20261117-001] token 估算按下限系数会低估英文，按上限又会高估

- **现象**：`utf8_bytes / 2.5` 对纯英文高估约 30%（英文实际 ≈4 字节/token）。
- **根因**：单一系数无法同时适配 CJK（≈2.2 字节/token）与拉丁（≈3.5–4 字节/token）。
- **正确做法**：按 Unicode 区间分段折算（`_CJK_RE` + 两个系数），不要用全局单系数。
  另注意：`count_tokens("a")` 这类短串经 `int()` 会变 0，**非空文本必须保底 1**，否则调用方可能死循环。
- **验证方式**：英文/中文/代码块/URL 密集四类样本各测一次，偏差应落在 ±15%。
- **相关文件**：`src/omni_article_markdown/utils.py`（`count_tokens`）

---

## [LOG-20261116-001] 站点改版后 extractor "静默失效"与"报错"的两种形态

- **现象 A（Cloudflare）**：报 `Failed to extract article content.` — 容器 `post-full-content` 全站消失。
- **现象 B（新浪财经）**：不报错，但输出 6KB 全是导航/页脚 — 没有 extractor 命中，落到 `DefaultExtractor`。
- **现象 C（火山引擎）**：报错，但原因不是改版，而是容器选择撞上了清理规则（见 LOG-20261123-001）。
- **正确做法**：排查顺序固定为
  1. `mdcli read <url>` 拿 HTML，`grep` 目标选择器是否还存在；
  2. 用 `ExtractorFactory.create(soup)` 打印**实际选中的 extractor 类名**——这一步能立刻区分 A/B 两类；
  3. 只有在确认 SSR 无正文时，才考虑 reader/Playwright。
- **验证方式**：`uv run python -c "from omni_article_markdown.extractor import ExtractorFactory; ..."`
- **相关文件**：`src/omni_article_markdown/extractor.py`（`ExtractorFactory`）

---

## [LOG-20261111-001] 站点改版后要保留旧模板兼容，而不是直接替换

- **现象**：oschina 改版成 SPA 后，旧选择器 `section.post-full-content`/`div.detail-box` 全部失效。
- **根因**：只支持单一模板，改版即失效；同时新模板需要浏览器渲染。
- **正确做法**：`article_container()` 返回**列表**（新 → 旧 → 兜底容器），
  让基类的顺序尝试机制承担降级；`can_handle()` 同时接受新旧站名后缀。
  同理，Cloudflare 也用 `[新容器, 旧容器, main]` 三档兜底。
- **验证方式**：用合成的旧模板 HTML 跑一次回归，确认仍能提取。
- **相关文件**：`src/omni_article_markdown/extractors/oschina.py`、`cloudflare_blog.py`

---

## [LOG-20261111-002] 标题污染：og:title 带站名后缀会连锁污染文件名

- **现象**：标题输出成 `计费说明--向量数据库VikingDB-火山引擎`、`… - OSCHINA - 开源 × AI · 开发者生态社区`。
- **根因**：`extract_title()` 默认走 `og:title`，而站点的 og:title 包含整串站名；
  `OmniArticleMarkdown.save()` 用 `to_snake_case(title)` 生成文件名，被一并污染。
- **正确做法**：在 extractor 里重写 `extract_title()`，优先取正文区的真实标题元素
  （`h1.blog-content-title`、`div.titleRow-DONu` 等），再 `return super().extract_title()` 兜底。
- **验证方式**：同时检查 Markdown 首行**和** `-s` 保存后的文件名。
- **相关文件**：`src/omni_article_markdown/extractors/*.py`、`omni_article_md.py`

---

## [LOG-20261111-003] 计划里的写法可能本身就是坑：以实测为准

- **现象**：多次出现"按计划照抄仓库既有写法 → 实测直接报错"，例如
  - 照抄 `-s` 的 `is_flag=False + flag_value + default=None` → click 8.3 下裸用报错（LOG-20261119-001）；
  - 照抄 `div[class="editor"]` → Playwright 永不匹配（LOG-20261119-002）；
  - 断言"正文需前端注入" → 实际 SSR 直出（LOG-20261123-002）。
- **根因**：照抄既有模式不等于该模式在当前依赖版本/当前 DOM 下成立。
- **正确做法**：**每一处"照抄"都要有一次最小验证**（10 行以内的 python 片段或一次 CLI 调用）。
  计划阶段写的"预期输出"必须在实施后逐条对照，不符就当场改计划，而不是绕过去。
- **验证方式**：实施后把计划验收标准逐条打勾，任何一条不符都写进本节。

---

## [LOG-20260513-001] 有 WAF 拦截的站点：必须用 Playwright，且匹配特征别绑 URL

- **现象**：`huxiu.com` 用纯 `requests` 拿不到正文——阿里云 WAF 对非浏览器请求返回反爬页面。
- **根因**：站点按 UA / JS 执行能力判定，静态请求直接被拦。
- **正确做法**：
  1. 在 `BrowserReader.TARGET_HOSTS` 加域名前缀（如 `https://www.huxiu.com/article`），
     让 Playwright 承担请求，从而带上完整浏览器指纹；
  2. `can_handle()` 用 `get_og_site_name() == "虎嗅网"` 这类**元数据特征**，不要用 URL 片段——
     URL 会随编辑策略变化；
  3. `extract_title()` 取 `h1.article__title`：这类站点的 `og:title` 常是更长的 SEO 变体
     （参见 LOG-20261111-002 的标题污染问题）。
- **验证方式**：`ReaderFactory.create(url)` 应返回 `BrowserReader`；正文首段与末段都要存在。
- **相关文件**：`src/omni_article_markdown/readers/browser.py`、`extractors/huxiu.py`

---

## [LOG-20260410-001] 缺少 canonical / OG 元数据的站点：用 og:title 后缀做匹配特征

- **现象**：`developers.googleblog.com` 没有稳定可用的 canonical，`is_matched_canonical()` 无法命中。
- **根因**：部分站点的 canonical 缺失或指向站点根域，不能作为唯一匹配键。
- **正确做法**：
  1. `can_handle()` 改用 `get_og_title(self.soup).endswith("- Google Developers Blog")`；
  2. 容器取 `div.blog-detail-container`；
  3. 清理谓词按站点版式**成组**覆盖：`tags-`、`summary-`、`author-`、`social-`、
     `navigation-`、`related-posts-` 六类容器——这类模板化博客的噪音结构高度固定。
- **验证方式**：`uv run python -c` 里跑 `ExtractorFactory.create(soup)` 应返回 `GoogleBlogExtractor`。
- **相关文件**：`src/omni_article_markdown/extractors/googleblog.py`、`utils.py`（`get_og_title`）

---

## 历史任务归档（原 `agents/logs.md`）

> 早期任务流水，仅供追溯。可复用的价值已提炼进上方教训条目。

| 编号 | 日期 | 主题 | 归档说明 |
| --- | --- | --- | --- |
| LOG-20260513-001 | 2026-05-13 | HuxiuExtractor + BrowserReader 支持 huxiu.com | 已提炼为上方同名教训条目 |
| LOG-20260410-001 | 2026-04-10 | GoogleBlogExtractor | 已提炼为上方同名教训条目（原文声称新增 `tests/test_googleblog_extractor.py`，该文件实际不存在，不予保留） |
| LOG-20260413-001 | 2026-04-13 | 新增 `.github/copilot-instructions.md` | 纯流程记录，无技术价值，仅保留编号 |

---
