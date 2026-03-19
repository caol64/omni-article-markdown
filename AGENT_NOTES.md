## 2026-03-19

- 开发 Snowflake 技术博客 extractor (`snowflake_blog.py`)
- Snowflake 博客识别方式：
  - 通过 canonical URL 中包含 `snowflake.com/en/blog` 来识别
  - 或通过特有的 `snowflake-blog-text` class 来识别
- Snowflake 博客的内容在 `div.snowflake-blog-text` 中

## 2026-03-18

- 开发飞书文档 extractor (`feishu.py`)
- 飞书文档识别方式：通过特有的 `wikiSSRBox`和`suite-doc` class 来识别，而不是依赖 URL
- 飞书文档的标题提取：优先从 `window.SERVER_DATA` 中提取，其次从`page-block-header__custom_icon` 提取
- 飞书文档的特殊标签转换：
  - `data-block-type="heading1/2/3/4/5/6"` -> `h1/h2/h3/h4/h5/h6`
  - `data-block-type="quote_container"` -> `blockquote`
  - `data-block-type="code"` -> `pre > code`
- 注意事项：
  - 飞书文档没有 `og:url` 标签，不能依赖 URL 识别
  - 飞书文档的内容在 `render-unit-wrapper` div 中
  - 飞书文档的 heading 块使用 `div` 标签加`data-block-type` 属性，需要转换为标准 HTML heading 标签才能被 parser 正确解析
  - 文本末尾可能包含特殊字符（如 `\u200b\u200c\u200d\ufeff`），需要清理
