# AGENTS.md

本项目是一个命令行工具：把网页文章转换成干净的 Markdown。

## 一、铁律（先读这条）

**只能使用 `uv`，严禁使用 `pip` / `pip3` / `python -m pip`。**

这些命令会把依赖装进**全局 Python 环境**，污染机器并让本地运行结果与 `uv.lock` 脱节。任何时候都不要。
`pip install` 失败的报错也不要去"修"，那是约束本身。

| 目的 | 正确写法 |
| --- | --- |
| 安装/同步依赖 | `uv sync` |
| 跑 CLI | `uv run mdcli <url>` |
| 跑测试 | `uv run pytest` |
| 跑单个测试 | `uv run pytest tests/test_parser.py::test_codeblock` |
| 格式化 | `uv run ruff format .` |
| 检查 | `uv run ruff check .` |
| 类型检查 | `uv run mypy src/omni_article_markdown` |
| 构建 | `uv build` |

临时写脚本验证也一样：`uv run python -c "..."`，不要 `python3 -c`。

## 二、精益尖叫架构（Lean Screaming Architecture）

本项目的目录结构必须**一眼看出业务意图**，而不是技术分层。

- **当前的三段式流水线就是骨架**：
  `reader`（拿 HTML）→ `extractor`（抽出正文）→ `parser`（转 Markdown）。
  讨论、命名、新增代码时，先问：**这段逻辑属于哪一段？** 而不是"放进 utils"。
- **垂直切片优先**：站点适配一律是
  `readers/<site>.py` 或 `extractors/<site>.py` 的**单个文件**，
  内含该站点所需的全部知识（匹配条件、容器、清理规则、预处理）。
  不要把某站点的细节泄漏到 `utils.py` / `parser.py` 等共用层。
- **共用层只放真正跨站点的东西**：`utils.py`（通用辅助）、`parser.py`（HTML→MD 引擎）、
  `extractor.py`（基类与工厂）。往共用层加代码前，确认至少两个站点需要它。
- **不改骨架换站点**：新增站点禁止修改 `omni_article_md.py` 的流水线顺序；
  靠工厂 + `can_handle()` 扩展。
- **删掉跑不通的抽象**：如果某层没有实际调用者，就删除，不要留"以后可能用"的空壳。

## 三、架构速览

```
mdcli <url>
  └─ OmniArticleMarkdown.parse()
       ├─ _read()            ReaderFactory → 首个匹配的 reader，否则 HtmlReader（本地文件走 FileReader）
       ├─ looks_like_markdown()? → 是则原样透传，不走后续
       ├─ _extract_article() ExtractorFactory → 首个匹配的 extractor，否则 DefaultExtractor
       └─ _parse_html()      HtmlMarkdownParser → 最终 Markdown
```

- 插件式发现：`readers/`、`extractors/` 下**新增模块即自动注册**，没有中心注册表。
- `can_handle()` 是**首个命中即停**，所以条件必须写窄，避免抢占别的站点。
- 输出后处理：`truncate.py`（`--truncate` 截断）、`markdown_detector.py`（纯 Markdown 透传）。
- `Cli` 选项封装：可选值选项统一用 `cli.py::_optional_value_option()`，别手写 `flag_value`。

## 四、常用工具与约定

- **技能手册**：动手前先读 `.agents/skills/` 下对应角色——
  `extractor-developer`（提取正文）、`reader-developer`（抓取 HTML）。它们是标准动作流程。
- **先用最轻的 reader**：默认 `requests`；只有确认 SSR 无正文时，才考虑 `BrowserReader`。
- **先容器后清理**：extractor 优先 `article_container()`，再考虑 `get_attrs_to_clean()`；
  DOM 结构归一（如 `div` 伪装标题、懒加载图片）放 `pre_handle_soup()`。
- **标题会连锁影响文件名**：`save()` 用 `to_snake_case(title)`，改 `extract_title()` 后
  要同时检查 Markdown 首行和保存的文件名。
- **测试风格**：`tests/` 下是内联 HTML 片段 + `make_soup` fixture 的小单测，
  不要写依赖真站的端到端测试。
- **默认不新增测试**，除非用户明确要求。

## 五、踩坑日志（长期记忆）

`.agents/docs/dev_logs.md` 记录**已踩过并已修正**的真实坑，是团队共享的长期记忆。

**开发前必做**：按关键词搜索它。例如改 `truncate.py` 前搜 `truncate`，
加 `BrowserReader` 配置前搜 `浏览器`、`selector`，新增 extractor 报错前搜 `Failed to extract`。

**开发后必做**：若踩到**新的、可泛化**的坑（换一个站点/模块仍会复现），按文件内的模板追加一节：
现象 → 根因 → 正确做法 → 验证方式 → 相关文件。

**不要写入**：一次性事实（某站点今天的选择器）。任务流水也不必单独记录——本文件只收可复用的教训，
历史任务见文末归档表。

## 六、Agent 工作流

1. 判断角色：`reader` 问题还是 `extractor` 问题（两者都涉及就按顺序处理）。
2. 读对应技能：`.agents/skills/<role>/SKILL.md`。
3. **搜索 `.agents/docs/dev_logs.md`**，看有没有现成的坑。
4. 探测：`uv run mdcli read <url>` 拿原始 HTML，确认正文是否在 SSR 里。
5. 编码：优先新增/修改单个站点文件，不改共用层。
6. 验证：`uv run mdcli <url>` 比对输出；再跑 `uv run ruff check .` 与 `uv run pytest`。
7. 有新坑就回写 `.agents/docs/dev_logs.md`。