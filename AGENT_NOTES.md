## 2026-03-31

- 修复 Twitter/X 长文段落结构问题
- 问题描述：
  - Twitter/X 的长文（Article）使用 Draft.js 编辑器渲染
  - 原始 HTML 没有 `<p>` 标签区分段落，而是使用 CSS 样式（`longform-unstyled` 等）在页面上进行分段
  - 导致抓取到的 markdown 所有内容都不分段，挤在一起
- 解决方案：
  - 在 `pre_handle_soup()` 方法中查找所有 class 包含 `longform` 的 div 元素
  - 用 `<p>` 标签包裹这些段落元素
  - 这样传到后续的 markdown 转换流程就能正确识别段落
- 技术细节：
  - Twitter/X 使用 `data-offset-key` 属性来标识不同的段落块
  - 每个段落是一个带有 `longform-unstyled` 或 `longform-header-*` 类的 div
  - 使用 BeautifulSoup 的 `class_` 参数配合 lambda 函数查找：`class_=lambda x: x and "longform" in str(x)`
  - 注意：不要使用 `any("longform" in c for c in x)`，因为 class 可能已经是字符串而不是列表

## 2026-03-27

- 开发 Twitter/X 推文提取器 (`twitter.py`)
- Twitter/X 识别方式：通过 `og:site_name` 为 "X (formerly Twitter)" 来识别
- Twitter/X 的特殊处理：
  - Twitter/X 使用 JavaScript 渲染，需要通过浏览器（playwright）来获取完整内容
  - 在 `BROWSER_TARGET_HOSTS` 中添加 `x.com/` 和 `twitter.com/`
  - 浏览器插件针对 Twitter/X 做了特殊处理：
    - 使用 `domcontentloaded` 而不是 `networkidle`（因为 Twitter 的连接可能永远不会 idle）
    - 等待 `[data-testid="tweet"]` 或 `article` 元素出现
    - 滚动页面以触发懒加载内容
- Twitter/X 的内容结构：
  - 推文容器：`<article>` 标签
  - 普通推文：在带有 `lang` 属性的 div 中
  - 长文（Thread/Article）：在 `public-DraftEditor-content` 或 `longform-unstyled` 类中
- 提取策略：
  - 优先查找 `public-DraftEditor-content` 类（长文）
  - 其次查找 `longform-unstyled` 类（长文段落）
  - 然后查找 `lang` 属性的 div（普通推文）
  - 最后查找包含较长文本的 div
- 注意事项：
  - Twitter 的 API 需要认证，无法直接调用
  - 需要等待足够的时间让 JavaScript 渲染完成
  - 长文可能包含多个段落，需要合并

## 2026-03-19

- 开发 Snowflake 技术博客 extractor (`snowflake_blog.py`)
- Snowflake 博客识别方式：
  - 通过 canonical URL 中包含 `snowflake.com/en/blog` 来识别
  - 或通过特有的 `snowflake-blog-text` class 来识别
- Snowflake 博客的内容在 `div.snowflake-blog-text` 中

- 开发飞书文档 extractor (`feishu.py`)
- 飞书文档识别方式：通过特有的 class 来识别（`wikiSSRBox`、`suite-body`、`suite-docx`、`is-suite`）
- 飞书文档的特殊处理：
  - 由于飞书文档使用虚拟滚动（virtual scrolling），只有可见区域的内容会被渲染到 DOM 中
  - 完整的 heading 数据存储在 `window.catalogRecordInfo.headingRecords` 中
  - `headingRecords` 是一个对象，key 为记录 ID，value 包含 `data.type`、`data.text`、`data.parent_id` 等字段
  - `text` 字段的结构：`data.text.initialAttributedTexts.text["0"]`
  - 通过查找 `data.type == "page"` 的记录获取 `children` 数组，其中包含按顺序排列的所有块 ID
  - 但 `children` 中只包含已渲染的 heading，未渲染的 heading 需要从 `headingRecords` 中提取并按文本中的数字排序
  - 使用 `_extract_heading_number` 方法从 heading 文本中提取数字（支持阿拉伯数字和中文数字）
  - 将提取到的 heading 补充到 DOM 中，然后统一转换为标准 HTML heading 标签
- 飞书文档的特殊标签转换：
  - `data-block-type="heading1/2/3/4/5/6"` -> `h1/h2/h3/h4/h5/h6`
  - `data-block-type="quote_container"` -> `blockquote`
  - `data-block-type="code"` -> `pre > code`
- 浏览器插件配置：
  - 在 `BROWSER_TARGET_HOSTS` 中添加 `waytoagi.feishu.cn/`
  - 对于飞书文档，直接使用 requests 获取 SSR HTML（而不是浏览器渲染），因为浏览器渲染会丢失 JavaScript 中的 heading 数据
- 注意事项：
  - 飞书文档没有 `og:url` 标签，不能依赖 URL 识别
  - 飞书文档的标题优先从 `window.SERVER_DATA` 中提取
  - 文本末尾可能包含特殊字符（如 `\u200b\u200c\u200d\ufeff`），需要清理
  - 飞书文档有两种渲染模式：wiki 模式（`wikiSSRBox`）和 suite 模式（`suite-body`）
  - 飞书文档可能有多个 `window.catalogRecordInfo`，其中一个是空的，需要查找包含完整 `headingRecords` 的那个
