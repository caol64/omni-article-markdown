---
name: "omni-article-markdown"
description: "将网页转换为干净的 Markdown。当用户要求把某篇文章/网页转成 Markdown、提取正文、抓取指定 URL 的文章内容，或提到 mdcli / 墨探 时使用。"
---

# 墨探 (omni-article-markdown)：网页文章转 Markdown

`mdcli` 是一个命令行工具，输入文章 URL，输出结构化、去噪后的 Markdown 文档。适用于博客、新闻、技术文档等内容型页面。

## 1. 前置检查与安装

先确认工具可用：

```bash
command -v mdcli || echo "NOT INSTALLED"
```

未安装时，任选一种方式安装（需要 Python ≥ 3.13）：

```bash
# pipx（推荐）
pipx install omni-article-markdown

# uv
uv tool install omni-article-markdown

# pip
pip install omni-article-markdown
```

Docker 环境（免装 Python，已内置浏览器栈）：

```bash
docker run --rm caol64/omnimd <url>
```

## 2. 基本用法

```bash
# 转换并输出到 stdout（parse 是默认子命令，可省略）
mdcli https://example.com/article

# 保存为 .md 文件（-s 不带值保存到当前目录；带路径则保存到该目录，文件名取自文章标题）
mdcli https://example.com/article -s
mdcli https://example.com/article -s /path/to/dir

# 仅获取原始 HTML（调试用，不做提取和转换）
mdcli read https://example.com/article

# 本地 HTML 文件也可以直接转换
mdcli /path/to/page.html

# 纯 Markdown 源（如 GitHub raw / gist raw）会被识别并原样输出，不做 HTML 解析和格式转换
mdcli https://raw.githubusercontent.com/user/repo/main/README.md

# agent 场景推荐：限制输出规模，防止长文撑爆上下文
# token 数为分段启发式估算（拉丁 ≈4 字节/token，CJK ≈2.2），误差约 ±10%；--truncate 不带数值时默认 800 tokens
mdcli <url> --truncate
mdcli <url> --truncate 1500
```

选项说明：

- `--no-verify-ssl`：跳过 SSL 证书校验（仅在目标站证书链异常时使用）。
- `-p, --prettify`（配合 `read`）：格式化输出 HTML。
- `--truncate [N]`：将输出的 Markdown 截断到约 N 个 token（省略 N 时默认 800）。截断在段落边界收尾，代码块/表格不会被劈坏，末尾以 `…[truncated]` 标记内容不完整。可与 `-s` 组合，保存的即截断后的内容。

## 3. 动态渲染站点

部分站点正文由 JS 渲染或有防爬策略。`mdcli` 会按需自动启用 Playwright 浏览器方案，并在首次使用时**自动安装 playwright 库和 Chromium**（无需手动操作，但首次运行较慢，需等待下载）。

判断方法：若 `mdcli read <url>` 返回的 HTML 中找不到正文文字，而浏览器打开正常，即属于此类——直接照常调用 `mdcli <url>` 即可，工具会自动处理。

## 4. 输出格式约定

成功时输出一篇完整的 Markdown 文档：

```markdown
# 文章标题

> 摘要（可选，来自 og:description）

正文……图片转为绝对 URL 的 ![](...)，代码块保留围栏，表格转为 GFM 表格。
```

- 退出码 `0` 表示成功；失败时 stderr 输出 `Error: ...` 且退出码非 `0`。
- 使用 `-s` 保存时，stdout 无内容，stderr 提示 `Article saved to: <绝对路径>`。

## 5. 故障处理

| 现象 | 处理 |
|---|---|
| `Error: Failed to extract article content.` | 该页面不适合作为文章提取（列表页/纯 JS 空壳）。先用 `mdcli read <url>` 确认 HTML 是否含正文；确属不支持的站点时，向用户说明并改用其他方式获取内容 |
| 网络超时 / SSL 错误 | 重试一次；证书问题可加 `--no-verify-ssl` |
| 输出混入导航/推荐等噪音 | 该站点尚未深度适配，记录 URL 反馈给项目 Issue：<https://github.com/caol64/omni-article-markdown/issues> |

## 6. 示例

```bash
mdcli https://simonwillison.net/2026/Nov/9/mysterious-beeps/
mdcli https://finance.sina.com.cn/wm/2026-11-16/doc-iniyxynv2270218.shtml -s
mdcli https://blog.cloudflare.com/dns-cache-memory-optimization-1111/
```

更多已适配站点见项目 README 的网站兼容列表。
